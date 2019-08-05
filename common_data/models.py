from __future__ import unicode_literals

import json
import os
import copy

from django.db import models

from latrom import settings
import subprocess
from background_task.models import Task
from common_data.utilities.mixins import ContactsMixin
from django.shortcuts import reverse
class PhoneNumber(models.Model):
    number = models.CharField(max_length=16)

class Person(models.Model):
    first_name = models.CharField(max_length =32)
    last_name = models.CharField(max_length =32)
    address = models.TextField(max_length =128, blank=True, default="")
    email = models.CharField(max_length =32, blank=True, default="")
    phone = models.CharField(max_length =16, blank=True, default="")

    class Meta:
        abstract = True

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

class SoftDeletionModel(models.Model):
    class Meta:
        abstract = True

    active = models.BooleanField(default=True)


    def delete(self):
        self.active = False
        self.save()

    def hard_delete(self):
        super().delete()

class Individual(ContactsMixin, Person, SoftDeletionModel):
    '''inherits from the base person class in common data
    represents clients of the business with entry specific details.
    the customer can also have an account with the business for credit 
    purposes
    A customer may be a stand alone individual or part of a business organization.
    '''
    phone_fields = ['phone', 'phone_two']
    email_fields = ['email']
    phone_two = models.CharField(max_length = 16,blank=True , default="")
    other_details = models.TextField(blank=True, default="")
    organization = models.ForeignKey('common_data.Organization', 
        on_delete=models.CASCADE,null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    
  
    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse("base:individual-detail", kwargs={"pk": self.pk})
    

class Note(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    author = models.ForeignKey('auth.User', on_delete=models.SET_NULL, 
        null=True)
    note = models.TextField()

    def __str__(self):
        return "{}({}): {}".format(self.timestamp.strftime("%d %b %y, %H:%M "), self.author, self.note)

class Organization(ContactsMixin, models.Model):
    phone_fields = ['phone']
    email_fields = ['email']

    legal_name = models.CharField(max_length=255)
    business_address = models.TextField(blank=True)
    website = models.CharField(max_length=255, blank=True)
    bp_number = models.CharField(max_length=64, blank=True)
    email=models.CharField(max_length=128, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    logo = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.legal_name

    @property 
    def members(self):
        return self.individual_set.all()

    def add_member(self, individual):
        individual.organization = self
        individual.save()

    def get_absolute_url(self):
        return reverse("base:organization-detail", kwargs={"pk": self.pk})
    

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class GlobalConfig(SingletonModel):
    DOCUMENT_THEME_CHOICES = [
        (1, 'Simple'),
        (2, 'Blue'),
        (3, 'Steel'),
        (4, 'Verdant'),
        (5, 'Warm')
    ]

    BACKUP_FREQUENCY_CHOICES = [
        ('D', 'Daily'),
        ('M', 'Monthly'),
        ('W', 'Weekly')
        ]

    LOGO_CHOICES = [
        (0, '3:2 (Medium rectangle)'),
        (1, '1:1 (Square)'),
        (2, '4:3 (Narrower Rectangle)'),
        (3, ':16:9 (Wide Rectangle)'),
    ]
    document_theme = models.IntegerField(
        choices= DOCUMENT_THEME_CHOICES, 
        default=1)
    currency = models.ForeignKey(
        'accounting.Currency', 
        blank=True, 
        on_delete=models.SET_NULL, 
        null=True)
    organization = models.ForeignKey(
        'common_data.organization',
        on_delete=models.SET_NULL, 
        null=True)
    payment_details = models.TextField(
        blank=True, 
        default="")
    application_version = models.CharField(
        max_length=16, 
        blank=True, 
        default="0.0.1")
    hardware_id = models.CharField(
        max_length=255, 
        blank=True, 
        default="")
    last_license_check = models.DateField(null=True)
    last_automated_service_run = models.DateTimeField(null=True, blank=True)
    use_backups = models.BooleanField(
        blank=True,
        default=False)
    backup_frequency = models.CharField(
        max_length=32, 
        choices=BACKUP_FREQUENCY_CHOICES, 
        default="D")
    verification_task_id = models.CharField(
        default="", 
        blank=True,
        max_length=255)
    is_configured = models.BooleanField(
        default=False
    )
    logo_aspect_ratio = models.PositiveSmallIntegerField(
        default=0, 
        choices=LOGO_CHOICES)
    
    
    def generate_hardware_id(self):
        result = subprocess.run('wmic csproduct get uuid', 
            stdout=subprocess.PIPE, shell=True)
        _id = result.stdout.decode('utf-8')
        _id = _id[_id.find('\n') + 1:]
        id = _id[:_id.find(' ')]

        return id    

    @property
    def task_mapping(self):
        mapping = {
            'D': Task.DAILY,
            'W': Task.WEEKLY,
            'M': Task.EVERY_4_WEEKS,
            '': Task.DAILY
        }
        return mapping[self.backup_frequency]

    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)

        #setup hardware id
        if self.hardware_id == "":
            self.hardware_id = self.generate_hardware_id()
            super().save(*args, **kwargs)


        #serialize and store in json file so settings.py can access
        json_config = os.path.join(settings.BASE_DIR, 'global_config.json')
        with open(json_config, 'w+') as fil:
            fields = copy.deepcopy(self.__dict__)
            del fields['hardware_id']
            del fields['last_license_check']
            del fields['last_automated_service_run']
            del fields['_state']
            json.dump(fields, fil)


    @property
    def logo_width(self):
        '''All logos share a heigh of 100 px, width is calculated as a ratio
        relative to this value.'''
        mapping = {
            0: 1.5,
            1: 1,
            2: 1.33,
            3: 1.78
        }

        return mapping[self.logo_aspect_ratio] * 100

    @classmethod
    def logo_url(cls):
        conf = cls.objects.first()
        if conf and conf.logo:
            return conf.logo.url
        return ""

    @property
    def business_address(self):
        return self.organization.business_address if self.organization else None

    @property
    def business_name(self):
        return self.organization.legal_name if self.organization else None

    @property
    def contact_details(self):
        return f"Phone: {self.organization.phone}"
        f"Email: {self.organization.email}" if self.organization else ""

    @property
    def logo(self):
        return self.organization.logo if self.organization else None
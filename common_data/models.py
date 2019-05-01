from __future__ import unicode_literals

import json
import os
import copy

from django.db import models

from latrom import settings
import subprocess
##%%
from common_data.utilities import db_util
from common_data.schedules import backup_db
from background_task.models import Task


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

class Individual(Person, SoftDeletionModel):
    '''inherits from the base person class in common data
    represents clients of the business with entry specific details.
    the customer can also have an account with the business for credit 
    purposes
    A customer may be a stand alone individual or part of a business organization.
    '''
    phone_two = models.CharField(max_length = 16,blank=True , default="")
    other_details = models.TextField(blank=True, default="")
    organization = models.ForeignKey('common_data.Organization', 
        on_delete=models.CASCADE,null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)
    
  
    def __str__(self):
        return self.full_name


class Note(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    author = models.ForeignKey('auth.User', on_delete=models.SET_NULL, 
        null=True)
    note = models.TextField()

    def __str__(self):
        return "{}({}): {}".format(self.timestamp.strftime("%d %b %y, %H:%M "), self.author, self.note)

class Organization(models.Model):
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
    # TODO personalize email settings for each user
    email_host = models.CharField(max_length=32, blank=True, default="")
    email_port = models.IntegerField(null=True, blank=True)
    email_user = models.CharField(max_length=32, blank=True, default="")
    # TODO secure email password
    email_password = models.CharField(max_length=255, blank=True, default="")
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
    use_backups = models.BooleanField(
        blank=True,
        default=False)
    backup_frequency = models.CharField(
        max_length=32, 
        choices=BACKUP_FREQUENCY_CHOICES, 
        default="D")
    backup_location_type = models.CharField(
        blank=True, 
        default="",
        max_length=255)
    backup_location = models.CharField(
        default="", 
        blank=True,
        max_length=255)
    verification_task_id = models.CharField(
        default="", 
        blank=True,
        max_length=255)
    is_configured = models.BooleanField(
        default=False
    )
    
    
    def generate_hardware_id(self):
        result = subprocess.run('wmic csproduct get uuid'.split(), stdout=subprocess.PIPE)
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
            '': 5
        }
        return mapping[self.backup_frequency]

    def save(self, *args, **kwargs):
        
        super().save(*args, **kwargs)
        
        if self.use_backups and self.backup_location == "":
            task = backup_db(repeat=self.task_mapping)
            #task = backup_db(repeat=10)
            
            self.backup_location = task.task_hash
            super().save(*args, **kwargs)

        print(self.backup_location)
        if not self.use_backups and self.backup_location != "":
            tasks = Task.objects.filter(task_hash=self.backup_location)
            if tasks.exists():
                tasks.delete()
                print('deleting task')
            
            self.backup_location = ""
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
            del fields['_state']
            json.dump(fields, fil)


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
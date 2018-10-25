from __future__ import unicode_literals

import json
import os

from django.db import models

from latrom import settings


class Person(models.Model):
    first_name = models.CharField(max_length =32)
    last_name = models.CharField(max_length =32)
    address = models.TextField(max_length =128, blank=True, default="")
    email = models.CharField(max_length =32, blank=True, default="")
    phone = models.CharField(max_length =16, blank=True, default="")

    class Meta:
        abstract = True


class Individual(Person):
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
    
    def delete(self):
        self.active = False
        self.save()

    def __str__(self):
        return self.first_name + " " + self.last_name


class Note(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    author = models.ForeignKey('auth.User', on_delete=None,)
    note = models.TextField()


class Organization(models.Model):
    legal_name = models.CharField(max_length=255)
    business_address = models.TextField(blank=True)
    website = models.CharField(max_length=255, blank=True)
    tax_clearance = models.CharField(max_length=64, blank=True)
    email=models.CharField(max_length=128, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    

    def __str__(self):
        return self.legal_name

    @property 
    def members(self):
        return self.individual_set.all()


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
    email_host = models.CharField(max_length=32, blank=True, default="")
    email_port = models.IntegerField(null=True)
    email_user = models.CharField(max_length=32, blank=True, default="")
    email_password = models.CharField(max_length=255, blank=True, default="")

    def save(self, *args, **kwargs):
        super(GlobalConfig, self).save(*args, **kwargs)
        #serialize and store in json file so settings.py can access
        json_config = os.path.join(settings.BASE_DIR, 'global_config.json')
        with open(json_config, 'w+') as fil:
            fields = self.__dict__
            del fields['_state']
            json.dump(fields, fil)
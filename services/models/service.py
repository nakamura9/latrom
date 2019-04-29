# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from common_data.utilities import time_choices
from common_data.models import SingletonModel

# Create your models here.

class ServicesSettings(SingletonModel):
    is_configured = models.BooleanField(default=False)
    

class Service(models.Model):
    # client and sales facing model
    name = models.CharField(max_length=255)
    description = models.TextField()
    flat_fee = models.DecimalField(max_digits=6, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey('services.ServiceCategory', 
        on_delete=models.SET_NULL, null=True,)
    procedure = models.ForeignKey('services.ServiceProcedure', 
        on_delete=models.CASCADE, null=True, blank=True)
    frequency = models.CharField(max_length = 16, 
                        choices = [("once", "Once off"),
                                    ("daily", "Daily"),
                                    ("weekly", "Weekly"),
                                    ("fortnightly", "Every 2 weeks"),
                                    ("monthly", "Monthly"),
                                    ("quarterly", "Every 3 Months"),
                                    ("bi-annually", "Every 6 Months"), 
                                    ("yearly", "Yearly")])
    is_listed = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.name

class ServiceCategory(models.Model):
    '''Used to organize services'''
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def service_count(self):
        return self.service_set.all().count()

#might rename 
class ServicePerson(models.Model):
    employee = models.OneToOneField('employees.Employee', null=True,
        on_delete=models.SET_NULL,)
    is_manager = models.BooleanField(default=False)
    can_authorize_equipment_requisitions = models.BooleanField(default=False)
    can_authorize_consumables_requisitions = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

    @property
    def name(self):
        return str(self.employee)

class ServiceTeam(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    manager = models.ForeignKey('services.ServicePerson', 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        related_name="service_team_manager")
    members = models.ManyToManyField('services.ServicePerson', 
        related_name="service_team_members")

    def __str__(self):
        return self.name

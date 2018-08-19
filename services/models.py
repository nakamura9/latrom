# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from common_data.utilities import time_choices

# Create your models here.
class Service(models.Model):
    # client and sales facing model
    name = models.CharField(max_length=255)
    description = models.TextField()
    flat_fee = models.DecimalField(max_digits=6, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey('services.ServiceCategory')
    procedure = models.ForeignKey('services.ServiceProcedure', null=True, blank=True)
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

    def create_work_order(self):
        pass

    def __str__(self):
        return self.name

class ServiceCategory(models.Model):
    '''Used to organize services'''
    name = models.CharField(max_length=64)
    parent = models.ForeignKey('services.ServiceCategory', blank=True, 
        null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    @property
    def children(self):
        return self.category_set.all()

class ServicesManager(models.Model):
    employee = models.ForeignKey('employees.Employee')
    can_authorize_equipment_requisitions = models.BooleanField(default=False)
    can_authorize_consumables_requisitions = models.BooleanField(default=False)

    def __str__(self):
        return self.employee.full_name

#might rename 
class ServicesPerson(models.Model):
    employee = models.ForeignKey('employees.Employee')

    def __str__(self):
        return self.employee.full_name

class ServiceTeam(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    manager = models.ForeignKey('services.ServicesManager', null=True, 
        blank=True)
    members = models.ManyToManyField('services.ServicesPerson')

class ServiceWorkOrder(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('progress', 'In progress'),
        ('completed', 'Completed'),
        ('authorized', 'Authorized'),
        ('declined', 'Declined')
        ]
    date = models.DateField()
    time = models.TimeField(choices = time_choices(
        '06:00:00', '18:30:00', '00:30:00'
        ))
    completed = models.DateTimeField(null=True, blank=True)
    expected_duration = models.DurationField(choices = time_choices(
        '00:00:00', '08:00:00', '00:30:00', delta=True
        ), null=True, blank=True) 
    actual_duration = models.DurationField(choices = time_choices(
        '00:00:00', '08:00:00', '00:30:00', delta=True
        ), null=True, blank=True)
    service_people = models.ManyToManyField('services.ServicesPerson', 
        blank=True)
    team = models.ForeignKey('services.ServiceTeam', null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    authorized_by = models.ForeignKey('employees.Employee')#filter queryset
    comments = models.TextField(blank=True)

class BaseRequisition(models.Model):
    class Meta:
        abstract = True

    date = models.DateField()
    warehouse = models.ForeignKey('inventory.WareHouse', default=1)
    department = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    
    

class EquipmentRequisition(BaseRequisition):
    requested_by = models.ForeignKey('employees.Employee', 
        related_name='requested_by')
    authorized_by = models.ForeignKey('employees.Employee', 
        related_name='authorized_by')#filter queryset
    released_by = models.ForeignKey('employees.Employee', 
        related_name='released_by')


class EquipmentRequisitionLine(models.Model):
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('poor', 'Poor'),
        ('broken', 'Not Functioning')
    ]
    equipment = models.ForeignKey('inventory.Equipment') 
    quantity = models.FloatField()
    quantity_returned = models.FloatField()
    requesting_condition = models.CharField(max_length=16, 
        choices=CONDITION_CHOICES)
    returned_condition = models.CharField(max_length=16, 
        choices=CONDITION_CHOICES)


class ConsumablesRequisition(BaseRequisition):
    requested_by = models.ForeignKey('employees.Employee', 
        related_name='consumable_requested_by')
    authorized_by = models.ForeignKey('employees.Employee', 
        related_name='consumable_authorized_by')#filter queryset
    released_by = models.ForeignKey('employees.Employee', 
        related_name='consumable_released_by')


class ConsumablesRequisitionLine(models.Model):
    consumable = models.ForeignKey('inventory.Consumable')
    unit = models.ForeignKey('inventory.UnitOfMeasure')
    quantity = models.FloatField()
    returned = models.FloatField(default=0.0)


class Task(models.Model):
    procedure = models.ForeignKey('services.ServiceProcedure')
    description = models.TextField()

class ServiceProcedure(models.Model):
    as_checklist = models.BooleanField(default=False, blank=True)
    name = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    required_equipment = models.ManyToManyField('inventory.Equipment', blank=True)
    required_consumables = models.ManyToManyField('inventory.Consumable', blank=True)

    @property
    def steps(self):
        return self.task_set.all().order_by('pk')
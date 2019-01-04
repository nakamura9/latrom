# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from common_data.utilities import time_choices


# Create your models here.
class Service(models.Model):
    # client and sales facing model
    name = models.CharField(max_length=255)
    description = models.TextField()
    flat_fee = models.DecimalField(max_digits=6, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ForeignKey('services.ServiceCategory', on_delete=None,)
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
    employee = models.OneToOneField('employees.Employee', on_delete=None,)
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
    manager = models.ForeignKey('services.ServicePerson', on_delete=None, 
        null=True, blank=True, related_name="service_team_manager")
    members = models.ManyToManyField('services.ServicePerson', 
        related_name="service_team_members")

    def __str__(self):
        return self.name

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
    description = models.TextField(blank=True, default="")
    completed = models.DateTimeField(null=True, blank=True)
    expected_duration = models.DurationField(choices = time_choices(
        '00:00:00', '08:00:00', '00:30:00', delta=True
        ), null=True, blank=True) 
    actual_duration = models.DurationField(choices = time_choices(
        '00:00:00', '08:00:00', '00:30:00', delta=True
        ), null=True, blank=True)
    service_people = models.ManyToManyField('services.ServicePerson', 
        blank=True)
    team = models.ForeignKey('services.ServiceTeam', on_delete=None, null=True, 
        blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, blank=True)
    authorized_by = models.ForeignKey('employees.Employee', 
        on_delete=models.CASCADE, null=True, 
        blank=True,
        limit_choices_to=Q(user__isnull=False))#filter queryset
    comments = models.TextField(blank=True)

    def __str__(self):
        return "%s: %d" % (self.date, self.pk)

class BaseRequisition(models.Model):
    class Meta:
        abstract = True

    date = models.DateField()
    warehouse = models.ForeignKey('inventory.WareHouse', 
        on_delete=models.CASCADE, default=1)
    department = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    
    def __str__(self):
        return '%s: %s' % (self.date, self.reference)

class EquipmentRequisition(BaseRequisition):
    requested_by = models.ForeignKey('employees.Employee', 
        on_delete=models.CASCADE, 
        related_name='requested_by')
    authorized_by = models.ForeignKey('employees.Employee', 
        related_name='authorized_by', on_delete=models.CASCADE, null=True)#filter queryset
    released_by = models.ForeignKey('employees.Employee', 
        related_name='released_by', on_delete=models.CASCADE, null=True)

    
class EquipmentRequisitionLine(models.Model):
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('poor', 'Poor'),
        ('broken', 'Not Functioning')
    ]
    equipment = models.ForeignKey('inventory.Equipment', on_delete=None,) 
    quantity = models.FloatField()
    quantity_returned = models.FloatField(default=0)
    requesting_condition = models.CharField(max_length=16, 
        choices=CONDITION_CHOICES)
    returned_condition = models.CharField(max_length=16, 
        choices=CONDITION_CHOICES, null=True)
    requisition = models.ForeignKey('services.EquipmentRequisition', 
        on_delete=models.CASCADE)

    def __str__(self):
        return str(self.equipment)

class ConsumablesRequisition(BaseRequisition):
    requested_by = models.ForeignKey('employees.Employee', 
        related_name='consumable_requested_by', on_delete=None)
    authorized_by = models.ForeignKey('employees.Employee', 
        related_name='consumable_authorized_by', on_delete=None, null=True)#filter queryset
    released_by = models.ForeignKey('employees.Employee', 
        related_name='consumable_released_by',on_delete=None, null=True)

class ConsumablesRequisitionLine(models.Model):
    consumable = models.ForeignKey('inventory.Consumable', on_delete=None,)
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=None)
    quantity = models.FloatField()
    returned = models.FloatField(default=0.0)
    requisition = models.ForeignKey('services.ConsumablesRequisition', 
        on_delete=models.CASCADE)

    def __str__(self):
        return str(self.consumable)


class Task(models.Model):
    procedure = models.ForeignKey('services.ServiceProcedure', 
        on_delete=models.CASCADE)
    description = models.TextField()
    
    def __str__(self):
        return self.description


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

    def __str__(self):
        return self.name
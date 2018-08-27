# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from common_data.models import SingletonModel
from inventory.models import Supplier
from invoicing.models import Customer
from employees.models import Employee
from common_data.utilities import time_choices
import datetime

class PlannerConfig(SingletonModel):
    number_of_agenda_items = models.PositiveIntegerField(default=10)
    autogenerate_events_from_models = models.BooleanField(default=False)

class Event(models.Model):
    REMINDER_CHOICES = [
        (datetime.timedelta(seconds=0), 'At event start'),
        (datetime.timedelta(minutes=15), '15 min before'),
        (datetime.timedelta(hours=1), '1 hour before'),
        (datetime.timedelta(hours=3), '3 hour before'),
        (datetime.timedelta(hours=6), '6 hours before'),
        (datetime.timedelta(days=1), '1 Day before'),
        (datetime.timedelta(days=3), '3 Days before'),
        (datetime.timedelta(days=7), '1 week before'),
        (datetime.timedelta(days=14), '2 weeks before'),
        (datetime.timedelta(days=30), '1 month before')

        
    ]
    
    TIME_CHOICES = time_choices('06:00:00','18:00:00','00:30:00')
    
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('high', 'High'),
        ('low', 'Low')
    ]

    date = models.DateField()
    reminder = models.DurationField(choices=REMINDER_CHOICES, default=datetime.timedelta(seconds=0))
    completed = models.BooleanField(default=False, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(choices=TIME_CHOICES, null=True, blank=True)
    end_time = models.TimeField(choices=TIME_CHOICES, null=True, blank=True)
    priority = models.CharField(max_length=8, choices=PRIORITY_CHOICES, default='normal')
    description = models.TextField(blank=True)
    label = models.CharField(max_length=32, blank=True) 
    icon = models.CharField(max_length=32, blank=True)
    participants = models.ManyToManyField(
        'planner.EventParticipant', 
        blank=True,
        related_name='participants')
    owner = models.ForeignKey('auth.User', on_delete=None)

    def add_participant(self, evt_type, pk):
        evt_mapping = {
            'supplier': 2,
            'employee': 0,
            'customer': 1
        }
        evt_type = evt_mapping[evt_type]
        if evt_type == 0:
            self.participants.create(
                participant_type = evt_type,
                employee=Employee.objects.get(pk=pk)
            )
        elif evt_type == 1:
            self.participants.create(
                participant_type = evt_type,
                customer=Customer.objects.get(pk=pk)
            )
        elif evt_type == 2:
            self.participants.create(
                participant_type = evt_type,
                supplier=Supplier.objects.get(pk=pk)
            )
        else:
            raise Exception('no type was specified')

    def complete(self):
        self.completed = True
        self.completion_time = datetime.datetime.now()
        self.save()


class EventParticipant(models.Model):
    PARTICIPANT_TYPES = [
        (0, 'Employee'),
        (1, 'Customer'),
        (2, 'Supplier')
    ]
    participant_type = models.PositiveSmallIntegerField(
        choices=PARTICIPANT_TYPES
        )
    employee = models.ForeignKey('employees.Employee', on_delete=None, null=True, blank=True)
    customer = models.ForeignKey('invoicing.Customer', on_delete=None, null=True, blank=True)
    supplier = models.ForeignKey('inventory.Supplier', on_delete=None,  null=True, blank=True)

    def __str__(self):
        if self.participant_type == 0:
            return str(self.employee)
        if self.participant_type == 1:
            return str(self.customer)
        if self.participant_type == 2:
            return str(self.supplier)
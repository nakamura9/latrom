# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models

from common_data.models import SingletonModel
from common_data.utilities import time_choices
from employees.models import Employee
from inventory.models import Supplier
from invoicing.models import Customer


class PlannerConfig(SingletonModel):
    number_of_agenda_items = models.PositiveIntegerField(default=10)
    autogenerate_events_from_models = models.BooleanField(default=False, 
        blank=True)

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
    ICON_CHOICES = [
        ('file-chart-line', 'Report'),
        ('truck', 'Delivery'),
        ('users', 'Meeting'),
        ('stopwatch', 'Deadline'),
        ('book', 'Training'),
        ('calendar', 'Event')
    ]

    date = models.DateField()
    reminder = models.DurationField(choices=REMINDER_CHOICES, 
        default=datetime.timedelta(seconds=0))
    completed = models.BooleanField(default=False, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(choices=TIME_CHOICES, default="06:00:00")
    end_time = models.TimeField(choices=TIME_CHOICES, default="06:00:00")
    priority = models.CharField(max_length=8, choices=PRIORITY_CHOICES, 
        default='normal')
    description = models.TextField(blank=True)
    label = models.CharField(max_length=32, blank=True) 
    icon = models.CharField(max_length=32, blank=True, choices=ICON_CHOICES)
    owner = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

    @property
    def participants(self):
        return EventParticipant.objects.filter(event=self)

    def add_participant(self, evt_type, pk):
        evt_mapping = {
            'supplier': 2,
            'employee': 0,
            'customer': 1
        }
        evt_type = evt_mapping[evt_type]
        if evt_type == 0:
            EventParticipant.objects.create(
                event=self,
                participant_type = evt_type,
                employee=Employee.objects.get(pk=pk)
            )
        elif evt_type == 1:
            EventParticipant.objects.create(
                event=self,
                participant_type = evt_type,
                customer=Customer.objects.get(pk=pk)
            )
        elif evt_type == 2:
            EventParticipant.objects.create(
                event=self,
                participant_type = evt_type,
                supplier=Supplier.objects.get(pk=pk)
            )
        else:
            raise Exception('no type was specified')

    def complete(self):
        self.completed = True
        self.completion_time = datetime.datetime.now()
        self.save()

    def __str__(self):
        return self.label


class EventParticipant(models.Model):
    PARTICIPANT_TYPES = [
        (0, 'Employee'),
        (1, 'Customer'),
        (2, 'Vendor')
    ]
    participant_type = models.PositiveSmallIntegerField(
        choices=PARTICIPANT_TYPES
        )
    employee = models.ForeignKey('employees.Employee', 
        on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey('invoicing.Customer', 
        on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.ForeignKey('inventory.Supplier', 
        on_delete=models.SET_NULL, null=True,  blank=True)
    event = models.ForeignKey('planner.event', on_delete=models.SET_NULL, 
        null=True)


    def __str__(self):
        if self.participant_type == 0:
            return str(self.employee)
        if self.participant_type == 1:
            return str(self.customer)
        if self.participant_type == 2:
            return str(self.supplier)
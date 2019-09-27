# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from dateutil.relativedelta import relativedelta

from django.db import models

from common_data.models import SingletonModel
from common_data.utilities import time_choices
from employees.models import Employee
import inventory
from django.shortcuts import reverse



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
    REPEAT_CHOICES = [
        (0, 'Never'),
        (1, 'Daily'),
        (2, 'Weekly'),
        (3, 'Monthly'),
        (4, 'Annually'),

    ]

    date = models.DateField()
    reminder = models.DurationField(choices=REMINDER_CHOICES, 
        default=datetime.timedelta(seconds=0))
    completed = models.BooleanField(default=False, blank=True)
    completion_time = models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(choices=TIME_CHOICES, default="08:00:00")
    end_time = models.TimeField(choices=TIME_CHOICES, default="09:00:00")
    priority = models.CharField(max_length=8, choices=PRIORITY_CHOICES, 
        default='normal')
    description = models.TextField(blank=True)
    repeat = models.PositiveSmallIntegerField(default=0, choices=REPEAT_CHOICES)
    repeat_active = models.BooleanField(default=False, blank=True)
    label = models.CharField(max_length=32, blank=True) 
    icon = models.CharField(max_length=32, blank=True, choices=ICON_CHOICES)
    owner = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    reminder_notification = models.ForeignKey('messaging.notification', 
        blank=True, null=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("planner:event-detail", kwargs={"pk": self.pk})
    

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
        participant = None 
        if evt_type == 0:
            participant = EventParticipant.objects.create(
                event=self,
                participant_type = evt_type,
                employee=Employee.objects.get(pk=pk)
            )
        elif evt_type == 1:
            from invoicing.models import Customer
            
            participant = EventParticipant.objects.create(
                event=self,
                participant_type = evt_type,
                customer=Customer.objects.get(pk=pk)
            )
        elif evt_type == 2:
            participant = EventParticipant.objects.create(
                event=self,
                participant_type = evt_type,
                supplier=inventory.models.Supplier.objects.get(pk=pk)
            )
        else:
            raise Exception('no type was specified')

        return participant

    
    def complete(self):
        self.completed = True
        self.completion_time = datetime.datetime.now()
        self.save()

    @property
    def repeat_string(self):
        mapping = dict(self.REPEAT_CHOICES)
        return mapping[self.repeat]

    def repeat_on_date(self, date):
        # eliminate past dates at the begining
        if self.date > date:
            return False 

        if self.repeat == 0:
            return False

        elif self.repeat == 1:
            return True

        elif self.repeat == 2:
            if self.date.weekday() == date.weekday():
                return True
            return False

        elif self.repeat == 3:
            if self.date.day == date.day:
                return True
            return False

        elif self.repeat == 4:
            if self.date.day == date.day and self.date.month == date.month:
                return True
            return False

        return False

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
            return f"Employee: {str(self.employee)}"
        if self.participant_type == 1:
            return f"Customer: {str(self.customer)}"
        if self.participant_type == 2:
            return f"Vendor: {str(self.supplier)}"

    @property
    def participant_pk(self):
        if self.participant_type == 0:
            return self.employee.pk
        if self.participant_type == 1:
            return self.customer.pk
        if self.participant_type == 2:
            return self.supplier.pk
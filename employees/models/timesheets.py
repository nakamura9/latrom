
import random
import datetime
from decimal import Decimal as D
from functools import reduce
from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person, SingletonModel, SoftDeletionModel
import planner
import accounting
import invoicing
from django.shortcuts import reverse


class EmployeeTimeSheet(models.Model):
    MONTH_CHOICES = [
        'January',
        'February',
        'March', 
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ] 
    YEAR_CHOICES = [
        (i, i) for i in range(2000, 2051)
    ] 
    employee = models.ForeignKey('employees.employee', on_delete=models.SET_NULL, null=True, 
        related_name='target')
    month = models.PositiveSmallIntegerField(choices=enumerate(MONTH_CHOICES, start=1))
    year = models.PositiveSmallIntegerField(choices=YEAR_CHOICES)
    recorded_by = models.ForeignKey('employees.employee', on_delete=models.SET_NULL, 
        related_name='recorder', null=True)
    complete=models.BooleanField(default=False, blank=True)

    @property
    def normal_hours(self):
        total = datetime.timedelta(seconds=0)
        for line in self.attendanceline_set.all():
            total += line.normal_time

        return total

    @property
    def overtime(self):
        total = datetime.timedelta(seconds=0)
        for line in self.attendanceline_set.all():
            total += line.overtime

        return total

    @property
    def lines(self):
        return AttendanceLine.objects.filter(timesheet=self).order_by('date')

    def get_absolute_url(self):
        return reverse("employees:timesheet-detail", kwargs={"pk": self.pk})
    
    


class AttendanceLine(models.Model):
    timesheet = models.ForeignKey('employees.EmployeeTimeSheet', on_delete=models.SET_NULL, null=True)
    date = models.DateField()
    time_in = models.TimeField(blank=True, null=True)
    time_out = models.TimeField(blank=True, null=True)
    lunch_duration = models.DurationField(null=True, blank=True)

    def to_datetime(self, time):
        return datetime.datetime.combine(self.date, time)
    @property
    def total_time(self):
        return self.to_datetime(self.time_out) - self.to_datetime(self.time_in)
    
    @property
    def working_time(self):
        return self.total_time - self.lunch_duration

    @property
    def normal_time(self):
        if (self.working_time.seconds / 3600) > 8:
            return datetime.timedelta(hours=8)
        
        return self.working_time

    @property
    def overtime(self):
        if (self.working_time.seconds / 3600) > 8:
            return self.working_time - datetime.timedelta(hours=8)
        
        return datetime.timedelta(seconds=0)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.lunch_duration is None:
            self.lunch_duration = self.timesheet.employee.pay_grade.lunch_duration
            self.save()

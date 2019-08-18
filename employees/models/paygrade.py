
import random
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal as D
from functools import reduce
import reversion
from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person, SingletonModel, SoftDeletionModel
import planner
import accounting
import invoicing
from employees.models.payroll_elements import PayrollDate
from employees.models.employee import Employee
from django.shortcuts import reverse

@reversion.register()    
class PayGrade(models.Model):
    '''
    This model describes the common pay features applied to a group of employees.
    It outlines their benefits such as leave days, salary, hourly rates and 
    allowances and their obligations such as their deductions.
    Commission, Allowances and Deductions are aggregate objects of this data model.

    properties
    -----------
    
    '''
    LUNCH_CHOICES = [
        (datetime.timedelta(minutes=15), '15 min.'),
        (datetime.timedelta(minutes=30), '30 min.'),
        (datetime.timedelta(minutes=45), '45 min.'),
        (datetime.timedelta(hours=1), '1 hr.')

    ]

    PAY_FREQUENCIES = [
        (0, 'Weekly'),
        (1, 'Bi-Monthly'),
        (2, 'Monthly')
    ]
    name = models.CharField(max_length=16)
    salary = models.FloatField(default=0)
    pay_frequency = models.PositiveSmallIntegerField(default=2, choices=PAY_FREQUENCIES)
    monthly_leave_days = models.FloatField(default=0)
    hourly_rate = models.FloatField(default=0)
    overtime_rate = models.FloatField(default=0)
    overtime_two_rate = models.FloatField(default=0)
    commission = models.ForeignKey('employees.CommissionRule', on_delete=models.SET_NULL,
        null=True, blank=True)
    allowances = models.ManyToManyField('employees.Allowance', blank=True)
    deductions = models.ManyToManyField('employees.Deduction', blank=True)
    payroll_taxes = models.ManyToManyField('employees.PayrollTax', blank=True)
    subtract_lunch_time_from_working_hours = models.BooleanField(default=False, blank=True)
    lunch_duration = models.DurationField(
        choices=LUNCH_CHOICES,
        default=datetime.timedelta(hours=1)
        )
    maximum_leave_days = models.FloatField(default=60.0)

    def __str__(self):
        return self.name

    @property
    def employees(self):
        return Employee.objects.filter(pay_grade=self)

    def frequency_string(self):
        mapping = dict(self.PAY_FREQUENCIES)
        return mapping[self.pay_frequency]
    
    def get_absolute_url(self):
        return reverse("employees:pay-grade-detail", kwargs={"pk": self.pk})
    

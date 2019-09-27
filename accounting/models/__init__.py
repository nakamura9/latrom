import datetime
from decimal import Decimal as D

from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import SingletonModel, SoftDeletionModel
from .currency import *
from .expenses import *
from .assets import *
from .books import *
from .transactions import *
from .accounts import *
from accounting.schedules import run_accounting_service
from background_task.models import Task
from planner.models import Event
class AccountingSettings(SingletonModel):
    ACCOUNTING_PERIODS = [
        (0, "Annually"),
        (1, "Monthly"),
        (2, "Weekly")
    ]
    start_of_financial_year = models.DateField()
    default_accounting_period = models.PositiveSmallIntegerField(
        choices=ACCOUNTING_PERIODS, default=1)
    currency_exchange_table = models.ForeignKey(
        'accounting.CurrencyConversionTable', 
        on_delete=models.SET_NULL, 
        null=True)
    default_bookkeeper = models.ForeignKey('accounting.Bookkeeper', null=True,  
        blank=True, on_delete=models.SET_NULL)
    equipment_capitalization_limit = models.DecimalField(max_digits=12, 
        decimal_places=2,default=0.0)
    is_configured = models.BooleanField(default=False)
    service_hash = models.CharField(max_length=255, default="", blank=True)
    active_currency = models.ForeignKey('accounting.currency', 
        on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.set_financial_year_reminder()

    def set_financial_year_reminder(self):
        if Event.objects.filter(
                date=self.start_of_financial_year,
                label__contains='financial year').exists():
            return
        evt = Event.objects.create(
            label='Start of financial year',
            description='Remember to close the books for the current financial' 
                'year in preparation for the new year.',
            date=self.start_of_financial_year,
            repeat=4, 
            repeat_active=True,
            icon='calendar',
            reminder=datetime.timedelta(days=30),
            end_time="17:00:00"
        )

        if not self.default_bookkeeper:
            return 
        evt.add_participant('employee', self.default_bookkeeper.employee.pk)

class Bookkeeper(SoftDeletionModel):
    '''
    mutable
    Model that gives employees access to the bookkeeping function of the 
    software such as order creation and the like.'''
    employee = models.OneToOneField('employees.Employee', 
        on_delete=models.SET_NULL, null=True, default=1, limit_choices_to=Q(user__isnull=False))
    can_create_journals = models.BooleanField(default=False, blank=True)
    can_create_orders_and_invoices = models.BooleanField(default=False, blank=True)
    can_record_expenses = models.BooleanField(default=False, blank=True)
    can_record_assets = models.BooleanField(default=False, blank=True)


    def __str__(self):
        return self.employee.full_name


class Tax(SoftDeletionModel):
    '''
    rate immutable, create new tax if tax rate changes
    Used in invoices and payroll, tax is a cost incurred as a
     percentage of income. Will implement more complex tax features as required
    '''
    name = models.CharField(max_length=64)
    rate = models.FloatField()

    def __str__(self):
        return self.name

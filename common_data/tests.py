from django.test import TestCase
from django.contrib.auth.models import User
from accounting.models import *
import datetime
from common_data import models
from django.core.management import call_command
TODAY = datetime.date.today()

def create_test_common_entities(cls):
    '''Creates common entities for multiple applications
    
    1. individual
    2. organization'''

    cls.individual = models.Individual.objects.create(
        first_name="test",
        last_name="last_name")

    cls.organization = models.Organization.objects.create(
        legal_name="business"
    )

def create_test_user(cls):
    '''creates a test user that can be logged in for view tests'''
    cls.user = User.objects.create_superuser('Testuser', 'admin@test.com', '123')
    cls.user.save()

def create_account_models(cls):
    '''creates common accounts models.
    
    1. Accounts:
        a. account_c - account that is commonly credited
        b. account_d - account that is commonly debited'''
    if Journal.objects.all().count() < 5:
        call_command('loaddata', 'accounting/fixtures/accounts.json', 
            'accounting/fixtures/journals.json')

    cls.account_c = Account.objects.create(
            name= 'Model Test Credit Account',
            balance=100,
            type='asset',
            description='Some description'
        )
    cls.account_d = Account.objects.create(
            name= 'Model Test Debit Account',
            balance=100,
            type='liability',
            description='Some description'
        )
    cls.journal = Journal.objects.create(
            name= 'Model Test Journal',
            description="test journal"
        )
    cls.tax = Tax.objects.create(
            name='model test tax',
            rate=10
        )
    
    cls.entry = JournalEntry.objects.create(
        memo='record of test entry',
            date=TODAY,
            journal =cls.journal
    )
    cls.entry.simple_entry(
            10,
            cls.account_c,
            cls.account_d,
        )
    
    cls.asset = Asset.objects.create(
        name='Test Asset',
        description='Test description',
        category = 0,
        initial_value = 100,
        debit_account = cls.account_d,
        depreciation_period = 5,
        init_date = TODAY,
        depreciation_method = 0,
        salvage_value = 20,
    )
    cls.expense = Expense.objects.create(
        date=TODAY,
        description = 'Test Description',
        category=0,
        amount=100,
        billable=False,
        debit_account=cls.account_d,
    )
    if AccountingSettings.objects.all().count() == 0:
        cls.config = AccountingSettings.objects.create(
            start_of_financial_year = TODAY,
            use_default_chart_of_accounts = True
        )
    else:
        cls.config = AccountingSettings.objects.first()
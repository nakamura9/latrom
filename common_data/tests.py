from django.test import TestCase
from django.contrib.auth.models import User
from accounting.models import *
import datetime

TODAY = datetime.date.today()

def create_test_user(cls):
    cls.user = User.objects.create(username='Testuser')
    cls.user.set_password('123')
    cls.user.save()
    print cls.user

def create_account_models(cls):
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
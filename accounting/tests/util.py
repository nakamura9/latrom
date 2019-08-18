import datetime

from django.test import TestCase
from accounting.util import AccountingTaskService
from accounting.models import (
    Account,
    Expense, 
    RecurringExpense,
    InterestBearingAccount,
    AccountingSettings,
    Asset,
    Bookkeeper
    )
from django.contrib.auth.models import User
import employees 
import datetime
from calendar import monthrange

class AccountingServiceTest(TestCase):
    fixtures = ['settings.json','common.json','journals.json', 'accounts.json']

    @classmethod 
    def setUpTestData(cls):
        employees.tests.model_util.EmployeeModelCreator(cls).create_employee()
        cls.service = AccountingTaskService()
        cls.bookkeeper = Bookkeeper.objects.create(employee=cls.employee)
        cls.employee.user = User.objects.create_user('user')
        cls.employee.save()
        

    def test_service_run(self):
        self.service.run()
        self.assertTrue(True)

    def test_run_recurring_expenses(self):
        usr = User.objects.create(username = "test_user")

        RecurringExpense.objects.create(
            cycle= 1,
            description='desc',
            category=0,
            amount=10,
            recorded_by=usr,
            reference="",
            debit_account=Account.objects.first()
        )

        RecurringExpense.objects.create(
            cycle= 1,
            description='desc',
            category=0,
            amount=10,
            recorded_by=usr,
            last_created_date=datetime.date.today() - \
                datetime.timedelta(days=2),
            debit_account=Account.objects.first(),
            reference=""
        )
        self.service.run_recurring_expenses()
        self.assertEqual(Expense.objects.all().count(), 1)

    def test_run_interest_on_accounts(self):
        InterestBearingAccount.objects.create(
            name='testaccount2',
            balance=100,
            type='asset',
            description="something",
            balance_sheet_category="current-assets",
            interest_rate=10,
            interest_interval=0,
            interest_method=0,
            date_account_opened=datetime.date.today() - \
                datetime.timedelta(days=40)    
        )
        self.service.run_interest_on_accounts()
        self.assertTrue(InterestBearingAccount.objects.first().balance != 100)

    def test_depreciate_assets(self):
        #create asset
        asset = Asset.objects.create(
            name='Test Asset',
            description='Test description',
            category = 1,
            initial_value = 100,
            credit_account = Account.objects.get(pk=1000),
            depreciation_period = 5,
            init_date = datetime.date.today() - datetime.timedelta(days=365),
            depreciation_method = 0,
            salvage_value = 20,
        )
        #get the month end
        today = datetime.date.today()
        
        monthend = monthrange(today.year, today.month)[1]
        self.service.today = datetime.date(today.year, today.month, monthend)
        self.service.depreciate_assets()


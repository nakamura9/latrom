import datetime

from django.test import TestCase
from accounting.util import AccountingTaskService
from accounting.models import (
    Account,
    Expense, 
    RecurringExpense,
    InterestBearingAccount
    )
from django.contrib.auth.models import User


class AccountingServiceTest(TestCase):
    fixtures = ['journals.json', 'accounts.json']

    @classmethod 
    def setUpTestData(cls):
        cls.service = AccountingTaskService()

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
        self.assertEqual(Expense.objects.all().count(), 2)

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

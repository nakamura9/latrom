# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal
import json
import os
import urllib

from django.shortcuts import reverse
from django.test import Client, TestCase

from accounting.models import *
from common_data.tests import create_account_models, create_test_user
from employees.tests.models import create_test_employees_models
from inventory.tests import create_test_inventory_models
from latrom import settings

settings.TEST_RUN_MODE = True
TODAY = datetime.date.today()


class SimpleModelTests(TestCase):
    # use fixtures later
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_employees_models(cls)
    
    def test_create_account(self):
        acc = Account.objects.create(name= 'Other Test Account',
            balance=200,
            type='asset',
            description='Some description')

        self.assertIsInstance(acc, Account)

    def test_create_bookkeeper(self):
        obj = Bookkeeper.objects.create(employee=self.employee)
        self.assertIsInstance(obj, Bookkeeper)

    def test_create_journal(self):
        obj = Journal.objects.create(name='Test Book')
        self.assertIsInstance(obj, Journal)

    def test_create_tax(self):
        obj=Tax.objects.create(
                name='sales tax',
                rate=15)
        
        self.assertIsInstance(obj, Tax)
        
    def test_create_debit(self):
        pre_bal = self.account_c.balance
        obj = Debit.objects.create(
            account= self.account_c,
            amount = 10,
            entry= self.entry
        )
        self.assertIsInstance(obj, Debit)
        self.assertEqual(self.account_c.balance, pre_bal - 10)

    def test_create_credit(self):
        pre_bal = self.account_c.balance
        obj = Credit.objects.create(
            account= self.account_c,
            amount = 10,
            entry= self.entry
        )
        self.assertIsInstance(obj, Credit)
        self.assertEqual(self.account_c.balance, pre_bal + 10)


    def test_create_asset(self):
        
        obj = Asset.objects.create(
            name='Test Asset',
            description='Test description',
            category = 0,
            initial_value = 100,
            debit_account = self.account_d,
            depreciation_period = 5,
            init_date = TODAY,
            depreciation_method = 0,
            salvage_value = 20,
        )
        self.assertIsInstance(obj, Asset)
        
    def test_asset_create_entry(self):
        pre_entry_debit_account_value = self.account_d.balance
        #initial value of asset = 100
        self.asset.create_entry()
        self.assertEqual(
            self.account_d.balance,
            pre_entry_debit_account_value - 100)

class ExpenseModelTests(TestCase):
    # use fixtures later
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        cls.recurring_entry = RecurringExpense.objects.create(
            cycle=7,
            expiration_date=TODAY + datetime.timedelta(days=10),
            start_date=TODAY,
            description = 'Test Description',
            category=0,
            amount=100,
            debit_account=cls.account_d)

    def test_create_expense(self):
        obj = Expense.objects.create(
            date=TODAY,
            description = 'Test Description',
            category=0,
            amount=100,
            billable=False,
            debit_account=self.account_d)
        self.assertIsInstance(obj, Expense)

    def test_create_recurring_expense(self):
        obj = RecurringExpense.objects.create(
            cycle=7,
            expiration_date=TODAY,
            start_date=TODAY,
            description = 'Test Description',
            category=0,
            amount=100,
            debit_account=self.account_d)
        self.assertIsInstance(obj, RecurringExpense)

    def test_recurring_expense_is_current(self):
        self.assertTrue(self.recurring_entry.is_current)


    def test_recurring_expense_entry(self):
        pre_entry_debit_balance = self.recurring_entry.debit_account.balance
        self.recurring_entry.create_entry()
        #the expense value is 100
        self.assertEqual(
            pre_entry_debit_balance - 100,
            self.recurring_entry.debit_account.balance)

class JournalEntryModelTests(TestCase):
    # use fixtures later
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)

    def test_create_entry(self):
        obj = JournalEntry.objects.create(
            memo='record of test entry',
            date=TODAY,
            journal =self.journal,
            reference = "test reference"
        )

        self.assertIsInstance(obj, JournalEntry)
        

    def test_entry_debit(self):
        pre_debit_total = self.entry.total_debits
        self.entry.debit(10, self.account_c)
        self.assertEqual(self.entry.total_debits, pre_debit_total + 10)

    def test_entry_credit(self):
        pre_total_credit = self.entry.total_credits
        self.entry.credit(10, self.account_c)
        self.assertEqual(self.entry.total_credits, pre_total_credit + 10)
        
    def test_simple_entry(self):
        pre_credit_bal = self.account_c.balance
        pre_debit_bal = self.account_d.balance
        self.entry.simple_entry(10, self.account_c, self.account_d)
        self.assertEqual(self.account_c.balance, pre_credit_bal + 10)
        self.assertEqual(self.account_d.balance, pre_debit_bal - 10)

    def test_entry_total_debits(self):
        self.assertIsNotNone(self.entry.total_debits)

    def test_entry_total_credits(self):
        self.assertIsNotNone(self.entry.total_credits)

    def test_entry_balanced(self):
        self.assertTrue(self.entry.balanced)

class AccountModelTests(TestCase):
    # use fixtures later
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)

    def test_create_account(self):
        obj = Account.objects.create(
            name= 'Test Account',
            balance=100,
            type='asset',
            description='Some description'
        )
        self.assertIsInstance(obj, Account)

    def test_create_interest_bearing_account(self):
        obj = InterestBearingAccount.objects.create(
            name= 'Test Interest Account',
            balance=100,
            type='asset',
            description='Some description',
            interest_rate= 6,
            interest_interval = 1,
            interest_method = 0
        )
        self.assertIsInstance(obj, InterestBearingAccount)

    def test_account_increment_decrement_account(self):
        acc_c_b4 = self.account_c.balance
        self.assertEqual(self.account_c.increment(10), acc_c_b4 + 10)
        self.assertEqual(self.account_c.decrement(10), acc_c_b4)

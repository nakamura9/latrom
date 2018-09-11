# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client
from django.shortcuts import reverse
import json 
import os 
import urllib
from .models import *
import datetime
import decimal
from latrom import settings

from common_data.tests import create_test_user
from inventory.tests import create_test_inventory_models
from common_data.tests import create_account_models

settings.TEST_RUN_MODE = True
TODAY = datetime.date.today()



class ModelTests(TestCase):
    # use fixtures later
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)

    def test_create_account(self):
        acc = Account.objects.create(name= 'Other Test Account',
            balance=200,
            type='asset',
            description='Some description')

        self.assertIsInstance(acc, Account)

    def test_create_journal(self):
        j = Journal.objects.create(name='Sales Book')

        self.assertIsInstance(j, Journal)

    def test_create_tax(self):
        t=Tax.objects.create(name='sales tax',
            rate=15)
        
        self.assertIsInstance(t, Tax)
        
    def test_create_entry(self):
        #get balances before transactions
        acc_c_b4 = self.account_c.balance
        acc_d_b4 = self.account_d.balance 
        trans = JournalEntry.objects.create(
            memo='record of test entry',
            date=TODAY,
            journal =self.journal,
            reference = "test reference"
        )
        trans.simple_entry(
            10,
            self.account_c,
            self.account_d,
        )

        self.assertTrue(isinstance(trans, JournalEntry))
        # includes the deduction from self.entry.debit
        self.assertEqual(self.account_c.balance, acc_c_b4 + 10)
        self.assertEqual(self.account_d.balance, acc_d_b4 - 10)

    def test_journal_entry_debit(self):
        pre_total_debit = self.entry.total_debits
        self.entry.debit(10, self.account_c)
        self.assertEqual(self.entry.total_debits, pre_total_debit + 10)

    def test_journal_entry_credit(self):
        pre_total_credit = self.entry.total_credits
        self.entry.credit(10, self.account_c)
        self.assertEqual(self.entry.total_credits, pre_total_credit + 10)

    def test_account_increment_decrement_account(self):
        acc_c_b4 = self.account_c.balance
        self.assertEqual(self.account_c.increment(10), acc_c_b4 + 10)
        self.assertEqual(self.account_c.decrement(10), acc_c_b4)

    def test_create_asset(self):
        acc_d_b4 = self.account_d.balance
        asset = Asset.objects.create(
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
        self.assertIsInstance(asset, Asset)
        #testing transaction
        self.assertEqual(self.account_d.balance, acc_d_b4 - 100)
    
    def test_create_expense(self):
        acc_d_b4 = self.account_d.balance
        expense = Expense.objects.create(
            date=TODAY,
            description = 'Test Description',
            category=0,
            amount=100,
            billable=False,
            debit_account=self.account_d,
        )

        self.assertIsInstance(expense, Expense)
        #test transaction 
        self.assertEqual(self.account_d.balance, acc_d_b4 -100)
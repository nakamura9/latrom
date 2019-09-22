# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal
import json
import os
import urllib

from django.shortcuts import reverse
from django.test import Client, TestCase
from decimal import Decimal as D

from accounting.models import *
from employees import models as employee_models
from common_data.tests import create_account_models, create_test_user
from employees.tests.models import create_test_employees_models
from latrom import settings
from django.contrib.auth.models import User

TODAY = datetime.date.today()


class SimpleModelTests(TestCase):
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

    def test_create_bookkeeper(self):
        employee = employee_models.Employee.objects.create(
            
            first_name='name',
            last_name='name',
        )
        obj = Bookkeeper.objects.create(employee=employee)
        self.assertIsInstance(obj, Bookkeeper)
        # for __str__
        self.assertEqual(str(obj), "name name")

    def test_delete_bookkeeper(self):
        #create another employee
        employee = employee_models.Employee.objects.create(
            
            first_name='name',
            last_name='name',
        )
        obj = Bookkeeper.objects.create(employee=employee)
        obj.delete()
        self.assertEqual(obj.active, False)

    def test_create_journal(self):
        obj = Journal.objects.create(name='Test Book')
        self.assertIsInstance(obj, Journal)

    def test_create_tax(self):
        obj=Tax.objects.create(
                name='sales tax',
                rate=15)
        
        self.assertIsInstance(obj, Tax)
        self.assertEqual(str(obj), 'sales tax')

    def test_delete_tax(self):
        obj=Tax.objects.create(
                name='sales tax',
                rate=15)
        obj.delete()
        self.assertFalse(obj.active)

    def test_create_debit(self):
        pre_bal = self.account_c.balance
        obj = Debit.objects.create(
            account= self.account_c,
            amount = 10,
            entry= self.entry
        )
        self.assertIsInstance(obj, Debit)
        self.assertEqual(str(obj), 'Debit')
        self.assertEqual(self.account_c.balance, pre_bal + 10)

    def test_create_credit(self):
        pre_bal = self.account_c.balance
        obj = Credit.objects.create(
            account= self.account_c,
            amount = 10,
            entry= self.entry
        )
        self.assertIsInstance(obj, Credit)
        self.assertEqual(str(obj), 'Credit')
        self.assertEqual(self.account_c.balance, pre_bal - 10)

    def test_transaction_execute(self):
        self.entry.draft = True
        self.entry.save()
        pre_bal = self.account_c.balance

        obj = Credit.objects.create(
            account= self.account_c,
            amount = 10,
            entry= self.entry
        )

        obj.execute()
        self.assertEqual(self.account_c.balance, pre_bal)
        
        self.entry.draft = False
        self.entry.save()

        obj.execute()
        self.assertEqual(self.account_c.balance, pre_bal - 10)



    def test_create_ledger(self):
        obj = Ledger.objects.create(
            name="Test Ledger"
        )
        self.assertIsInstance(obj, Ledger)

    def test_create_workbook(self):
        obj = WorkBook.objects.create(
            name="Test Book"
        )
        self.assertIsInstance(obj, WorkBook)
    
    def test_create_adjustment(self):
        wkbk = WorkBook.objects.create(
            name="Test Book"
        )
        obj = Adjustment.objects.create(
            entry=self.entry,
            adjusting_entry=self.entry,
            workbook = wkbk,
            description='description on adjustment',
            created_by=self.bookkeeper
        )


class AssetTests(TestCase):
    # use fixtures later
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        PAST = TODAY - datetime.timedelta(days=732)
        cls.old_asset = Asset.objects.create(
            name='Test Asset',
            description='Test description',
            category = 0,
            initial_value = 100,
            credit_account = cls.account_d,
            depreciation_period = 5,
            init_date = PAST,
            depreciation_method = 0,
            salvage_value = 20,
        )
    
    def test_create_asset(self):    
        obj = Asset.objects.create(
            name='Test Asset',
            description='Test description',
            category = 0,
            initial_value = 100,
            credit_account = self.account_d,
            depreciation_period = 5,
            init_date = TODAY,
            depreciation_method = 0,
            salvage_value = 20,
        )
        self.assertIsInstance(obj, Asset)
        self.assertEqual(str(obj), 'Test Asset')

    def test_asset_create_entry(self):
        pre_entry_debit_account_value = self.account_d.balance
        self.asset.create_entry()
        self.assertEqual(
            self.account_d.balance,
            pre_entry_debit_account_value + 100)

    def test_asset_account(self):
        self.assertIsInstance(self.asset.account, Account)

    def test_asset_salvage_date(self):
        self.assertIsInstance(self.asset.salvage_date, datetime.date)

    def test_asset_timedelta_years(self):
        self.assertEqual(self.old_asset._timedelta, 2)

    def test_asset_category_string(self):
        self.assertEqual(self.asset.category_string, 'Land')

    def test_asset_total_depreciation(self):
        self.assertEqual(self.old_asset.total_depreciation, 32)

    def test_asset_current_value(self):
        self.assertEqual(self.old_asset.current_value, 68)


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
        self.assertEqual(obj.cycle_string, 'Weekly')
        self.assertIsInstance(str(obj), str)

    def test_expense_account_property(self):
        self.assertIsInstance(self.expense.expense_account, Account)

    def test_expense_entry(self):
        self.expense.create_entry()
        self.assertIsInstance(self.expense.entry, JournalEntry)

    def test_expense_category_string(self):
        self.assertEqual(self.expense.category_string, "Advertising")

    def test_recurring_expense_is_current(self):
        self.assertTrue(self.recurring_entry.is_current)

    def test_recurring_expense_standalone_expense(self):
        self.assertIsInstance(self.recurring_entry.create_standalone_expense(), 
            Expense)

    def test_recurring_expense_related_payments(self):
        self.recurring_entry.create_standalone_expense()
        self.assertTrue(self.recurring_entry.related_payments.count() != 0)


class JournalEntryModelTests(TestCase):
    # use fixtures later
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        cls.usr = User.objects.create(username = "test_user")
        

    def test_create_entry(self):
        obj = JournalEntry.objects.create(
            memo='record of test entry',
            date=TODAY,
            journal =self.journal,
            created_by = self.usr
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
        self.assertEqual(self.account_c.balance, pre_credit_bal - 10)
        self.assertEqual(self.account_d.balance, pre_debit_bal -10)

    def test_entry_total_debits(self):
        self.assertIsNotNone(self.entry.total_debits)

    def test_entry_total_credits(self):
        self.assertIsNotNone(self.entry.total_credits)

    def test_entry_balanced(self):
        self.assertTrue(self.entry.balanced)

    def test_compare_transactions(self):
        '''compares date of creation'''
        pre_bal = self.account_c.balance
        
        j = JournalEntry.objects.create(
            memo='record of test entry',
            date=TODAY,
            journal =self.journal,
            created_by = self.usr
        )

        j.credit(10, self.account_c)

        j_2 = JournalEntry.objects.create(
            memo='record of test entry',
            date=TODAY + datetime.timedelta(days=1),
            journal =self.journal,
            created_by = self.usr
        )

        j_2.credit(10, self.account_c)

        self.assertTrue(
            Credit.objects.get(entry=j) < Credit.objects.get(entry=j_2))
        
        #revert
        self.account_c.balance = pre_bal
        self.account_c.save()

    def test_primary_credit(self):
        j = JournalEntry.objects.create(
            memo='record of test entry',
            date=TODAY,
            journal =self.journal,
            created_by = self.usr
        )
        self.assertTrue(j.primary_credit is None)
        
        j.credit(10, self.account_c)
        
        self.assertTrue(j.primary_credit is not None)

    def test_primary_debit(self):
        j = JournalEntry.objects.create(
            memo='record of test entry',
            date=TODAY,
            journal =self.journal,
            created_by = self.usr
        )
        self.assertTrue(j.primary_debit is None)
        
        j.debit(10, self.account_c)
        
        self.assertTrue(j.primary_debit is not None)

    def test_delete_journal(self):
        j = Journal.objects.create(
            name='test journal',
            description='test description'
        )
        j.delete()
        self.assertFalse(j.active)

    def test_entries_over_period(self):
        NEXT_WEEK = TODAY + datetime.timedelta(days=7)
        j = JournalEntry.objects.create(
            memo='record of test entry',
            date=NEXT_WEEK,
            journal =self.journal,
            created_by = self.usr
        )
        entries = self.journal.get_entries_over_period(
            NEXT_WEEK - datetime.timedelta(days=1),
            NEXT_WEEK + datetime.timedelta(days=1))

        self.assertEqual(entries.count(), 1)

    def test_verify_entry(self):
        obj = JournalEntry.objects.create(
            memo='record of test entry',
            date=TODAY,
            journal =self.journal,
            created_by = self.usr
        )
        pre_c_bal = Account.objects.get(pk=self.account_c.pk).balance

        obj.credit(10, Account.objects.get(pk=self.account_c.pk))

        obj.verify()
        self.assertFalse(obj.draft)
        self.assertEqual(
            Account.objects.get(pk=self.account_c.pk).balance, pre_c_bal - 10)

        self.assertIsInstance(obj, JournalEntry)

    

class AccountModelTests(TestCase):
    # use fixtures later
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        cls.interest_account = InterestBearingAccount.objects.create(
            name= 'Test Interest Account',
            balance=100,
            type='asset',
            description='Some description',
            interest_rate= 5,
            interest_interval = 1,
            interest_method = 0
        )
        cls.basic_account = Account.objects.create(
            name= 'Test Account',
            balance=100,
            type='asset',
            description='Some description'
        )

    def  setUp(self):
        self.basic_account.balance=100
        self.basic_account.save()
        self.interest_account.balance=100
        self.interest_account.save()

    def test_create_account(self):
        obj = Account.objects.create(
            name= 'Test Account',
            balance=100,
            type='asset',
            description='Some description'
        )
        self.assertIsInstance(obj, Account)

    def test_account_credit_balance(self):
        
        self.assertEqual(self.basic_account.credit, D(0))
        self.assertEqual(self.basic_account.debit, D(100))

    def test_account_total_debit(self):
        self.assertIsInstance(self.basic_account.total_debit(), D)

    def test_account_total_credit(self):
        self.assertIsInstance(self.basic_account.total_credit(), D)

    def test_account_debit_balance(self):
        self.basic_account.balance = -100
        self.basic_account.save()
        self.assertEqual(self.basic_account.debit, -D(100))
        self.assertEqual(self.basic_account.credit, D(0))
    
    def test_delete_account(self):
        obj = Account.objects.create(
            name= 'Test Account',
            balance=100,
            type='asset',
            description='Some description'
        )
        obj.delete()
        self.assertEqual(obj.active, False)


    def test_account_children(self):
        obj = Account.objects.create(
            name= 'Test Account',
            balance=100,
            type='asset',
            description='Some description',
            parent_account=self.account_d
        )

        self.assertEqual(self.account_d.children.count(), 1)
        obj.delete()


    def test_account_control_balance(self):
        balance = Account.objects.get(pk=self.account_d.pk).balance
        obj = Account.objects.create(
            name= 'Test Account',
            balance=100,
            type='asset',
            description='Some description',
            parent_account=self.account_d
        )

        self.assertTrue(
            Account.objects.get(pk=self.account_d.pk).control_balance > balance)
        obj.delete()



    def test_account_increment_decrement_account(self):
        acc_c_b4 = self.account_c.balance
        self.assertEqual(self.account_c.increment(10), acc_c_b4 + 10)
        self.assertEqual(self.account_c.decrement(10), acc_c_b4)

    def test_create_interest_bearing_account(self):
        obj = InterestBearingAccount.objects.create(
            name= 'Test Interest Account',
            balance=100,
            type='asset',
            description='Some description',
            interest_rate= 5,
            interest_interval = 1,
            interest_method = 0
        )
        self.assertIsInstance(obj, InterestBearingAccount)


    def test_add_interest_to_interest_bearing_account(self):
        self.interest_account.add_interest()
        self.assertEqual(self.interest_account.balance, 105)

    def test_interest_bearing_account_interest_calculation(self):
        self.assertEqual(self.interest_account.interest_per_interval, 5)


    def test_interest_bearing_account_should_earn_interest(self):
        NEXT_YEAR = TODAY + datetime.timedelta(366)
        self.assertFalse(self.interest_account.should_receive_interest(TODAY))
        self.assertTrue(self.interest_account.should_receive_interest(
            NEXT_YEAR
        ))

        # if has last interest earned date 
        self.interest_account.last_interest_earned_date = TODAY
        self.interest_account.save()
        self.assertTrue(self.interest_account.should_receive_interest(
            NEXT_YEAR))

    def test_account_balance_type(self):
        asset = Account.objects.get(pk=1000)#cash
        self.assertEqual(asset.balance_type, "debit")
        
        liability = Account.objects.get(pk=2004)#loans payable
        self.assertEqual(liability.balance_type, "credit")
    
    def test_account_balance_on_date(self):
        date = datetime.date.today() - datetime.timedelta(days=7)
        self.assertEqual(self.basic_account.balance_on_date(date), 100)

    def test_account_balance_over_period(self):
        today = datetime.date.today()
        date = today - datetime.timedelta(days=7)
        self.assertEqual(
            self.basic_account.balance_over_period(date, today), 
                0)


class CurrencyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.currency = Currency.objects.create(
            name="Test",
            symbol="$"
        )
        cls.currency_table = CurrencyConversionTable.objects.create(
            name="table",
            reference_currency=cls.currency
        )
    
    def test_create_currency(self):
        obj = Currency.objects.create(
            name="Dollar",
            symbol="$"
        )
        self.assertIsInstance(obj, Currency)
        self.assertEqual(str(obj), "Dollar")

    def test_create_conversion_table(self):
        obj = CurrencyConversionTable.objects.create(
            name="table",
            reference_currency=self.currency
        )
        self.assertIsInstance(obj, CurrencyConversionTable)
        self.assertEqual(str(obj), 'table')

    def test_currency_conversion_line(self):
        obj = CurrencyConversionLine.objects.create(
            currency=self.currency,
            exchange_rate= 4,
            conversion_table=self.currency_table
        )
        self.assertIsInstance(obj, CurrencyConversionLine)


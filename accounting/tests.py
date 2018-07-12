# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, Client
from django.shortcuts import reverse
import json 
import os 
import urllib
from models import *
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


class ViewTests(TestCase):
    fixtures = ['accounts.json', 'journals.json']
    

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        create_test_user(cls)
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_inventory_models(cls)
        
        cls.ACCOUNT_DATA = {
                'name': 'Other Test Account',
                'balance': 100,
                'type': 'asset',
                'description': 'Test Description',
                'balance_sheet_category': 'expense'
            }

        cls.ENTRY_DATA = {
            'reference': 'some test ref',
            'memo':'record of test entry',
            'date':TODAY,
            'journal' :cls.journal.pk,
            'amount': 100,
            'debit': cls.account_d.pk,
            'credit': cls.account_c.pk
        }

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_dashboard(self):
        resp = self.client.get(reverse('accounting:dashboard'))
        self.assertTrue(resp.status_code==200)

    #EMPLOYEES

    
    #ENTRIES
    def test_get_entry_form(self):
        resp = self.client.get(reverse('accounting:create-entry'))
        self.assertTrue(resp.status_code==200)

    def test_get_compound_entry_form(self):
        resp = self.client.get(reverse('accounting:compound-entry'))
        self.assertTrue(resp.status_code==200)

    def test_post_compound_entry_form(self):
        COMPOUND_DATA = self.ENTRY_DATA
        n = JournalEntry.objects.all().count()
        COMPOUND_DATA['items[]'] = urllib.quote(json.dumps({
            'debit': 1,
            'amount':100,
            'account': self.account_c.pk
            }))
        resp = self.client.post(reverse('accounting:compound-entry'),
            data=COMPOUND_DATA)
        self.assertTrue(resp.status_code==302)

        #test transaction effect on account
        self.assertEqual(JournalEntry.objects.latest('pk').total_debits, 100)

    def test_post_entry_form(self):
        resp = self.client.post(reverse('accounting:create-entry'),
            data=self.ENTRY_DATA)
        self.assertTrue(resp.status_code==302)
        
    def test_get_entry_detail(self):
        resp = self.client.get(reverse('accounting:entry-detail', 
            kwargs={'pk': self.entry.pk}))
        self.assertTrue(resp.status_code==200)

    #ACCOUNTS

    def test_get_account_form(self):
        resp = self.client.get(reverse('accounting:create-account'))
        self.assertTrue(resp.status_code==200)

    def test_post_account_form(self):
        resp = self.client.post(reverse('accounting:create-account'),
            data=self.ACCOUNT_DATA)
        self.assertTrue(resp.status_code==302)

    def test_post_account_update_form(self):
        resp = self.client.post(reverse('accounting:account-update',
            kwargs={
                'pk': self.account_c.pk
            }),
            data=self.ACCOUNT_DATA)
        self.assertTrue(resp.status_code==302)

    def test_get_account_list(self):
        resp = self.client.get(reverse('accounting:account-list'))
        self.assertTrue(resp.status_code==200)

    def test_get_account_detail(self):
        resp = self.client.get(reverse('accounting:account-detail',
            kwargs={
                'pk': self.account_c.pk
            }))
        self.assertTrue(resp.status_code==200)

    def test_get_account_update(self):
        resp = self.client.get(reverse('accounting:account-update',
            kwargs={
                'pk': self.account_c.pk
            }))
        self.assertTrue(resp.status_code==200)

    #MISC ITEMS
    

    def test_get_transfer_form(self):
        resp = self.client.get(reverse('accounting:transfer'))
        self.assertTrue(resp.status_code == 200)

    

    def test_get_cash_sale(self):
        resp = self.client.get(reverse('accounting:non-invoiced-cash-sale'))
        self.assertTrue(resp.status_code == 200)

    def test_POST_cash_sale(self):
        resp = self.client.post(reverse('accounting:non-invoiced-cash-sale'),
            data={
                'date': TODAY,
                'comments': 'Test Comments',
                'sold_from': self.warehouse.pk,
                'items[]': urllib.quote(
                    json.dumps({
                        'code': self.item.pk,
                        'quantity':1,
                        'discount': 10
                        })
                    )
                })
        self.assertTrue(resp.status_code == 302)
        #1 item with 10% discount @ $10
        self.assertEqual(JournalEntry.objects.latest('pk').total_debits, 9)
    
    #JOURNALS

    def test_get_journal_form(self):
        resp = self.client.get(reverse('accounting:create-journal'))
        self.assertTrue(resp.status_code == 200)

    def test_post_journal_form(self):
        resp = self.client.post(reverse('accounting:create-journal'),
            data={
                'name': 'Other Test Journal',
                'start_period': TODAY,
                'end_period': TODAY + datetime.timedelta(days=30),
                'description': 'some test description'
            })
        
        self.assertTrue(resp.status_code == 302)

    def test_get_journal_list(self):
        resp = self.client.get(reverse('accounting:journal-list'))
        self.assertTrue(resp.status_code == 200)
    
    def test_get_journal_detail(self):
        resp = self.client.get(reverse('accounting:journal-detail',
            kwargs={
                'pk': self.journal.pk
            }))

    
    #CONFIG 
    def test_get_config_form(self):
        resp = self.client.get(reverse('accounting:config'))
        self.assertTrue(resp.status_code == 200)

    def test_post_config_form(self):
        resp = self.client.post(reverse('accounting:config'),
            data={
                'start_of_financial_year': '06/01/2018',
                'use_default_account_names': True,
                'direct_payment_journal': self.journal.pk,
                'cash_sale_account': self.account_c.pk,
                'direct_payment_account': self.account_c.pk})

        self.assertTrue(resp.status_code == 302)

    #Direct payments
    def test_get_direct_payment_list(self):
        resp = self.client.get(reverse('accounting:direct-payment-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_direct_payment_form(self):
        resp = self.client.get(reverse('accounting:direct-payment'))
        self.assertEqual(resp.status_code, 200)

    def test_post_payment_form(self):
        sup_b = self.supplier.account.balance
        resp = self.client.post(reverse('accounting:direct-payment'),
            data={
               'date':TODAY,
               'paid_to': self.supplier.pk,
               'account_paid_from': self.account_c.pk,
               'method': 'cash',
               'amount': 100,
               'reference': 'DPMT',
               'notes': 'Some Note'

            })
        self.assertEqual(resp.status_code, 302)
        # test transaction impact on accounts
        self.assertEqual(JournalEntry.objects.latest('pk').total_debits, 100)

    #asset and expense views tests
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
from inventory.tests import create_test_inventory_models
from latrom import settings

settings.TEST_RUN_MODE = True
TODAY = datetime.date.today()

class CommonViewTests(TestCase):
    fixtures = ['accounts.json', 'employees.json', 'journals.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_inventory_models(cls)
        cls.PAYMENT_DATA = {
               'date':TODAY,
               'paid_to': cls.supplier.pk,
               'account_paid_from': cls.account_c.pk,
               'method': 'cash',
               'amount': 100,
               'reference': 'DPMT',
               'notes': 'Some Note'
            }
        cls.CASH_SALE_DATA = {
            'date': TODAY,
            'comments': 'Test Comments',
            'sold_from': cls.warehouse.pk,
            'items[]': urllib.parse.quote(
                json.dumps({
                    'id': cls.product.pk,
                    'quantity':1,
                    'discount': 10
                    })
                )
            }

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_dashboard(self):
        resp = self.client.get(reverse('accounting:dashboard'))
        self.assertTrue(resp.status_code==200) 

    def test_get_transfer_form(self):
        resp = self.client.get(reverse('accounting:transfer'))
        self.assertTrue(resp.status_code == 200)

    def test_get_cash_sale(self):
        resp = self.client.get(reverse('accounting:non-invoiced-cash-sale'))
        self.assertTrue(resp.status_code == 200)

    def test_POST_cash_sale(self):
        resp = self.client.post(reverse('accounting:non-invoiced-cash-sale'),
            data=self.CASH_SALE_DATA)
        self.assertTrue(resp.status_code == 302)
        #1 item with 10% discount @ $10
        self.assertEqual(JournalEntry.objects.latest('pk').total_debits, 9)
    
    def test_get_config_form(self):
        resp = self.client.get(reverse('accounting:config', kwargs={
            'pk': 1}))
        self.assertTrue(resp.status_code == 200)

    def test_post_config_form(self):
        resp = self.client.post(reverse('accounting:config', kwargs={
            'pk':1
        }),
            data={
                'start_of_financial_year': '06/01/2018',
                })

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
            data=self.PAYMENT_DATA)
        self.assertEqual(resp.status_code, 302)
        # test transaction impact on accounts
        self.assertEqual(JournalEntry.objects.latest('pk').total_debits, 100)



class JournalEntryViewTests(TestCase):
    fixtures = ['accounts.json', 'employees.json','journals.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_inventory_models(cls)
    
        cls.ENTRY_DATA = {
            'reference': 'some test ref',
            'memo':'record of test entry',
            'date':TODAY,
            'journal' :cls.journal.pk,
            'amount': 100,
            'debit': cls.account_d.pk,
            'credit': cls.account_c.pk
        }
        cls.JOURNAL_DATA = {
                'name': 'Other Test Journal',
                'start_period': TODAY,
                'end_period': TODAY + datetime.timedelta(days=30),
                'description': 'some test description'
            }

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_entry_form(self):
        resp = self.client.get(reverse('accounting:create-entry'))
        self.assertTrue(resp.status_code==200)

    def test_post_entry_form(self):
        resp = self.client.post(reverse('accounting:create-entry'),
            data=self.ENTRY_DATA)
        self.assertTrue(resp.status_code==302)

    def test_get_compound_entry_form(self):
        resp = self.client.get(reverse('accounting:compound-entry'))
        self.assertTrue(resp.status_code==200)

    def test_post_compound_entry_form(self):
        COMPOUND_DATA = self.ENTRY_DATA
        n = JournalEntry.objects.all().count()
        COMPOUND_DATA['items[]'] = urllib.parse.quote(json.dumps({
            'debit': 1,
            'amount':100,
            'account': self.account_c.pk
            }))
        resp = self.client.post(reverse('accounting:compound-entry'),
            data=COMPOUND_DATA)
        self.assertTrue(resp.status_code==302)

        #test transaction effect on account
        self.assertEqual(JournalEntry.objects.latest('pk').total_debits, 100)

    def test_get_entry_detail(self):
        resp = self.client.get(reverse('accounting:entry-detail', 
            kwargs={'pk': self.entry.pk}))
        self.assertTrue(resp.status_code==200)

    def test_get_journal_form(self):
        resp = self.client.get(reverse('accounting:create-journal'))
        self.assertTrue(resp.status_code == 200)

    def test_post_journal_form(self):
        resp = self.client.post(reverse('accounting:create-journal'),
            data=self.JOURNAL_DATA)
        
        self.assertTrue(resp.status_code == 302)

    def test_get_journal_list(self):
        resp = self.client.get(reverse('accounting:journal-list'))
        self.assertTrue(resp.status_code == 200)
    
    def test_get_journal_detail(self):
        resp = self.client.get(reverse('accounting:journal-detail',
            kwargs={
                'pk': self.journal.pk
            }))

class AccountViewTests(TestCase):
    fixtures = ['accounts.json','employees.json', 'journals.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
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

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')


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


class TestReportViews(TestCase):
    fixtures = ['accounts.json', 'employees.json','journals.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        cls.client = Client()
        cls.statement_period = {
                'default_periods': 0,
              'start_period': (TODAY - datetime.timedelta(days=30)).strftime(
                  '%m/%d/%Y'),
              'end_period': TODAY.strftime('%m/%d/%Y'),  
            }
    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_inventory_models(cls)


    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_balance_sheet_page(self):
        resp = self.client.get(reverse('accounting:balance-sheet'))
        self.assertEqual(resp.status_code, 200)

    def test_get_income_statement_page(self):
        resp = self.client.get(reverse('accounting:income-statement'),
            data=self.statement_period)
        self.assertEqual(resp.status_code, 200)

    def test_get_income_statement_form_page(self):
        resp = self.client.get(reverse('accounting:income-statement-form'))
        self.assertEqual(resp.status_code, 200)

    #income statement form view has no post

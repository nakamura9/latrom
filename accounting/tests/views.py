# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal
import json
import os
import urllib

from django.shortcuts import reverse
from django.test import Client, TestCase
from django.test.client import RequestFactory
from accounting.models import *
from common_data.tests import create_account_models, create_test_user, create_test_common_entities
from inventory.tests import create_test_inventory_models
from latrom import settings
from employees.models import Employee 
from django.contrib.auth.models import User
from accounting import views 

TODAY = datetime.date.today()

class CommonViewTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'employees.json', 'journals.json', 'settings.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_common_entities(cls)
        create_test_user(cls)
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
        cls.tax = Tax.objects.create(
            name="TEst",
            rate=10
        )
        cls.currency = Currency.objects.create(
            name='Test',
            symbol='$'
        )
        cls.currency_table = CurrencyConversionTable.objects.create(
            name='Base',
            reference_currency=cls.currency
        )
        

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_dashboard(self):
        resp = self.client.get(reverse('accounting:dashboard'))
        self.assertTrue(resp.status_code==302)
        config = AccountingSettings.objects.first()
        config.is_configured=True
        config.save()
        resp = self.client.get(reverse('accounting:dashboard'))
        self.assertTrue(resp.status_code==200) 
        config.is_configured=False
        config.save()

    def test_accounting_async_dashboard(self):
        resp = self.client.get(reverse('accounting:async-dashboard'))
        self.assertTrue(resp.status_code, 200)


    def test_get_transfer_form(self):
        resp = self.client.get(reverse('accounting:transfer'))
        self.assertTrue(resp.status_code == 200)


    def test_get_create_tax(self):
        resp = self.client.get(reverse('accounting:create-tax'))
        self.assertTrue(resp.status_code==200) 

    def test_get_tax_list_page(self):
        resp = self.client.get(reverse('accounting:tax-list'))
        self.assertTrue(resp.status_code==200) 

    def test_get_tax_update_page(self):
        resp = self.client.get(reverse('accounting:update-tax', kwargs={
            'pk': self.tax.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_tax_update_page(self):
        resp = self.client.post(reverse('accounting:update-tax', kwargs={
            'pk': self.tax.pk
        }), data={'name': 'Tax Name'})
        self.assertEqual(resp.status_code, 302)

    def test_post_create_tax(self):
        resp = self.client.post(reverse('accounting:create-tax'), data={
            'name': 'Income tax',
            'rate': 15
        })
        self.assertTrue(resp.status_code==302) 

    def test_get_config_page(self):
        resp = self.client.get(reverse('accounting:config', kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_config_page(self):
        resp = self.client.post(reverse('accounting:config', kwargs={'pk': 1}),
            data={
                'start_of_financial_year': TODAY,
                'currency_exchange_table': self.currency_table.pk,
                'default_accounting_period': 0,
                'active_currency': 1,
                'equipment_capitalization_limit': 200
            })
        self.assertEqual(resp.status_code, 302)
        
    def test_get_direct_payment_page(self):
        resp = self.client.get(reverse('accounting:direct-payment'))
        self.assertEqual(resp.status_code, 200)

    def test_post_direct_payment_page(self):
        resp = self.client.post(reverse('accounting:direct-payment'),
            data=self.PAYMENT_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_supplier_direct_payment_page(self):
        resp = self.client.get(reverse('accounting:direct-payment-supplier',
            kwargs={
                'supplier': 1
            }
        ))
        self.assertEqual(resp.status_code, 200)


    def test_post_direct_payment_supplier_page(self):
        return
        #strange bug
        resp = self.client.post(reverse('accounting:direct-payment-supplier',
            kwargs={
                'supplier': 1
            }),
            data=self.PAYMENT_DATA)


class JournalEntryViewTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'employees.json','journals.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)
        create_account_models(cls)
        create_test_inventory_models(cls)
        create_test_common_entities(cls)
    
        cls.ENTRY_DATA = {
            'reference': 'some test ref',
            'memo':'record of test entry',
            'date':TODAY,
            'journal' :cls.journal.pk,
            'amount': 100,
            'debit': cls.account_d.pk,
            'credit': cls.account_c.pk,
            'created_by': cls.user.pk
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
            'account': "{} - Account - s".format(self.account_c.pk) 
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
        self.assertEqual(resp.status_code, 200)

    def test_get_journal_entries_list(self):
        resp = self.client.get(reverse('accounting:journal-entries',
            kwargs={
                'pk': self.journal.pk
            }))
        self.assertEqual(resp.status_code, 200)

    def test_verify_journal_entry(self):
        resp = self.client.get(reverse('accounting:verify-entry', kwargs={
            'pk': self.entry.pk
        }))
        self.assertEqual(resp.status_code, 302)

    def test_get_journal_report_form(self):
        resp = self.client.get(reverse('accounting:journal-form', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_journal_report_view(self):        
        resp = self.client.get(reverse('accounting:journal-report'), data={
            'default_periods': 3,
            'start_period': "",
            'end_period': "",
            'journal': 1
        })

        self.assertEqual(resp.status_code, 200)

    def test_journal_report_pdf(self):
        kwargs = {
            'start': (datetime.date.today() - datetime.timedelta(days=365)).strftime("%d %B %Y"),
            'end': datetime.date.today().strftime("%d %B %Y"),
            'journal': 1
        }
        req = RequestFactory().get(reverse(
            'accounting:journal-report-pdf', kwargs=kwargs))
        resp = views.JournalReportPDFView.as_view()(req, **kwargs)

        self.assertEqual(resp.status_code, 200)

        

class AccountViewTests(TestCase):
    fixtures = ['common.json','accounts.json','employees.json', 'journals.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)
        create_account_models(cls)
        create_test_inventory_models(cls)
        create_test_common_entities(cls)
    
        cls.ACCOUNT_DATA = {
                'name': 'Other Test Account',
                'balance': 100,
                'type': 'asset',
                'description': 'Test Description',
                'balance_sheet_category': 'non-current-assets'
            }

        cls.end = datetime.date.today()
        cls.start = cls.end - datetime.timedelta(days=30)

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

    def test_get_account_update_form(self):
        resp = self.client.get(reverse('accounting:account-update',
            kwargs={
                'pk': self.account_c.pk
            }),
            )
        self.assertTrue(resp.status_code==200)
    
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

    def test_get_account_entry_list_credit(self):
        resp = self.client.get(reverse('accounting:account-credits', 
            kwargs={'pk': 1000}))
        self.assertTrue(resp.status_code==200)

    def test_get_account_entry_list_debits(self):
        resp = self.client.get(reverse('accounting:account-debits', 
            kwargs={'pk': 1000}))
        self.assertTrue(resp.status_code==200)

    def test_get_account_report_form(self):
        resp = self.client.get(reverse('accounting:account-report-form', kwargs={
            'pk': 1000
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_account_report_view(self):        
        resp = self.client.get(reverse('accounting:account-report'), data={
            'default_periods': 3,
            'start_period': "",
            'end_period': "",
            'account': 1000
        })

        self.assertEqual(resp.status_code, 200)

    def test_account_pdf_view(self):
        start = urllib.parse.quote(self.start.strftime("%d %B %Y"))
        end = urllib.parse.quote(self.end.strftime("%d %B %Y"))
        
        kwargs={
            'start': start,
            'end': end,
            'account': 1000
        }
        req = RequestFactory().get(reverse('accounting:account-report-pdf', 
            kwargs=kwargs))
        resp = views.AccountReportPDFView.as_view()(req, **kwargs)
        self.assertEqual(resp.status_code, 200)


class TestReportViews(TestCase):
    fixtures = ['accounts.json', 'employees.json','journals.json', 
        'common.json','invoicing.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.client = Client()
        cls.statement_period = {
                'default_periods': 0,
              'start_period': (TODAY - datetime.timedelta(days=30)).strftime(
                  '%m/%d/%Y'),
              'end_period': TODAY.strftime('%m/%d/%Y'),  
            }


    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)
        create_account_models(cls)
        create_test_inventory_models(cls)
        create_test_common_entities(cls)
        cls.end = datetime.date.today()
        cls.start = cls.end - datetime.timedelta(days=30)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_balance_sheet_page(self):
        resp = self.client.get(reverse('accounting:balance-sheet'))
        self.assertEqual(resp.status_code, 200)

    def test_get_balance_sheet_pdf_page(self):
        req = RequestFactory().get(reverse('accounting:balance-sheet-pdf'))
        resp = views.BalanceSheetPDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_get_income_statement_page(self):
        resp = self.client.get(reverse('accounting:profit-and-loss'),
            data=self.statement_period)
        self.assertEqual(resp.status_code, 200)

    def test_get_income_statement_form_page(self):
        resp = self.client.get(reverse('accounting:profit-and-loss-form'))
        self.assertEqual(resp.status_code, 200)

    def test_get_balance_sheet_csv_report(self):
        resp = self.client.get(reverse('accounting:balance-sheet-csv'))
        self.assertEqual(resp.status_code, 200)

    def test_get_trial_balance_csv(self):
        resp = self.client.get(reverse('accounting:trial-balance-csv'))
        self.assertEqual(resp.status_code, 200)

    def test_get_profit_and_loss_csv(self):
        
        
        resp = self.client.get(reverse('accounting:profit-and-loss-csv', kwargs={
            'start': urllib.parse.quote(self.start.strftime("%d %B %Y")),
            'end':urllib.parse.quote(self.end.strftime("%d %B %Y"))
        }))
        self.assertEqual(resp.status_code, 200)

    def test_account_csv(self):
        resp = self.client.get(reverse('accounting:account-report-csv', kwargs={
            'start': urllib.parse.quote(self.start.strftime("%d %B %Y")),
            'end':urllib.parse.quote(self.end.strftime("%d %B %Y")),
            'account': 1000
        }))
        self.assertEqual(resp.status_code, 200)

    def test_journal_csv_report(self):
        resp = self.client.get(reverse('accounting:journal-report-csv', kwargs={
            'start': urllib.parse.quote(self.start.strftime("%d %B %Y")),
            'end':urllib.parse.quote(self.end.strftime("%d %B %Y")),
            'journal': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_trial_balance_page(self):
        resp = self.client.get(reverse('accounting:trial-balance'))
        self.assertEqual(resp.status_code, 200)

    def test_get_trial_balance_pdf(self):
        req = RequestFactory().get(reverse('accounting:trial-balance-pdf'))
        resp = views.TrialBalancePDFView.as_view()(req)
        
        self.assertEqual(resp.status_code, 200)

    def test_profit_and_loss_pdf(self):
        kwargs = {
            'start': (datetime.date.today() \
                - datetime.timedelta(days=365)).strftime('%d %B %Y'),
            'end': datetime.date.today().strftime('%d %B %Y')
        }
        req = RequestFactory().get(reverse('accounting:profit-and-loss-pdf', kwargs=kwargs))
        resp = views.ProfitAndLossReportPDFView.as_view()(req, **kwargs)
        
        self.assertEqual(resp.status_code, 200)


class TestCurrencyViews(TestCase):
    fixtures = ['common.json']
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls.client = Client()


    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)
        cls.currency = Currency.objects.create(
            name='Test',
            symbol='$'
        )
        cls.currency_table = CurrencyConversionTable.objects.create(
            name='Base',
            reference_currency=cls.currency
        )

        cls.currency_table_line = CurrencyConversionLine.objects.create(
            currency=cls.currency,
            exchange_rate=1.5,
            conversion_table=cls.currency_table
        )
        create_test_common_entities(cls)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_currency_converter_view(self):
        resp = self.client.get(reverse('accounting:currency-converter'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_currency_exchange_table(self):
        # no get
        resp = self.client.post(reverse('accounting:create-exchange-table'),    
            data={
                'name': 'Test',
                'reference_currency': self.currency.pk
            })

        self.assertEqual(resp.status_code, 302)

    def test_create_currency(self):
        resp = self.client.get(reverse('accounting:create-currency'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_currency(self):
        resp = self.client.post(reverse('accounting:create-currency'),
            data={
                'name': 'Test',
                'symbol': '$'
            })
        self.assertEqual(resp.status_code, 302)

    def test_update_currency(self):
        resp = self.client.get(reverse('accounting:update-currency',
            kwargs={
                'pk': self.currency.pk
            }))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_currency(self):
        resp = self.client.post(reverse('accounting:update-currency',
            kwargs={
                'pk': self.currency.pk
            }),
            data={
                'name': 'Test',
                'symbol': '$'
            })
        self.assertEqual(resp.status_code, 302)

    def test_currency_conversion_line_create_get(self):
        resp = self.client.get(reverse(
            'accounting:create-currency-conversion-line'))
        self.assertEqual(resp.status_code, 200)

    def test_currency_conversion_line_create_post(self):
        resp = self.client.post(reverse(
            'accounting:create-currency-conversion-line'),
            data={
                'currency': self.currency.pk,
                'exchange_rate': 1,
                'conversion_table': self.currency_table.pk 
            })
        self.assertEqual(resp.status_code, 302)


    def test_currency_conversion_line_update_get(self):
        resp = self.client.get(reverse(
            'accounting:update-currency-conversion-line', 
            kwargs={
                'pk': self.currency_table_line.pk
            }))
        self.assertEqual(resp.status_code, 200)

    def test_currency_conversion_line_update_post(self):
        resp = self.client.post(reverse(
            'accounting:update-currency-conversion-line', 
            kwargs={
                'pk': self.currency_table_line.pk
            }),
            data={
                'currency': self.currency.pk,
                'exchange_rate': 1,
                'conversion_table': self.currency_table.pk 
            })
        self.assertEqual(resp.status_code, 302)


    def test_update_reference_currency_functional_view(self):
        currency_two = Currency.objects.create(
            name='two',
            symbol='t'
        )
        resp = self.client.get('/accounting/api/update-reference-currency/%d/%d' % (
            self.currency_table.pk,
            currency_two.pk
            )
        )
        self.assertEqual(json.loads(resp.content)['status'], 'ok')


    def test_create_exchange_table_conversion_line_function(self):
        resp = self.client.post('/accounting/create-conversion-line',
            data={
                'table_id': self.currency_table.pk,
                'currency_id': self.currency.pk,
                'rate': 1.5
            })

    def test_exchange_rate(self):

        resp = self.client.post(
            '/accounting/api/update-exchange-rate/%d' % 
                self.currency_table_line.pk, data={
                   'rate': 2.5 
                })

        self.assertEqual(json.loads(resp.content)['status'], 'ok')

    def test_currency_conversion_line_serializer(self):
        resp = self.client.post('/accounting/api/currency-conversion-line', data={
            'currency': self.currency.pk,
            'exchange_rate': 2,
            'conversion_table': self.currency_table.pk
        })
        self.assertEqual(resp.status_code, 301)

    def test_currency_conversion_table_serializer(self):
        resp = self.client.post('/accounting/api/currency-conversion-table', data={
            'name': 'table',
            'reference_currency': self.currency.pk,
        })
        self.assertEqual(resp.status_code, 301)

    def test_currency_exchange_table_conversion_line(self):
        resp = self.client.post('/accounting/api/create-conversion-line', data={
            'table_id': self.currency_table.pk,
            'currency_id': self.currency.pk,
            'rate': 4.5
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content)['status'], 'ok')


class AccountingWizardTests(TestCase):
    fixtures = ['accounts.json', 'settings.json', 'journals.json', 'common.json', 'employees.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client()
        create_test_user(cls)

    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_accounting_wizard(self):
        config_data = {
            '0-start_of_financial_year': datetime.date.today(),
            '0-default_accounting_period': 0,
            '0-currency_exchange_table': 1,
            '0-active_currency': 1,
            'config_wizard-current_step': 0,
            '0-equipment_capitalization_limit': 200
        }

        employee_data = {
            '1-first_name': 'first',
            '1-last_name': 'last',
            '1-leave_days': 1,
            '1-pin': 1000,
            'config_wizard-current_step': 1,
        }

        bookkeeper_data = {
            '2-employee': 1,
            'config_wizard-current_step': 2,
        }

        tax_data = {
            '3-name': 'name',
            '3-rate': 10,
            'config_wizard-current_step': 3,

        }

        data_list = [config_data, employee_data, bookkeeper_data, tax_data]

        for step, data in enumerate(data_list, 1):
            try:
                resp = self.client.post(reverse('accounting:config-wizard'), data=data)
                if step == len(data_list):
                    self.assertEqual(resp.status_code, 302)
                    
                else:
                    self.assertEqual(resp.status_code, 200)

            except ValueError:
                pass

class AssetViewTests(TestCase):
    fixtures = ['common.json', 'settings.json', 'accounts.json', 'journals.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)

        cls.asset = Asset.objects.create(
            name='Test Asset',
            description='Test description',
            category = 0,
            initial_value = 100,
            credit_account = Account.objects.get(pk=1000),
            depreciation_period = 5,
            init_date = datetime.date.today(),
            depreciation_method = 0,
            salvage_value = 20,
        )
        cls.data = {
            'name': 'name',
            'description': 'description',
            'category': 0,
            'initial_value': 100,
            'credit_account':1000,
            'depreciation_period': 5,
            'init_date': datetime.date.today(),
            'depreciation_method': 0,
            'salvage_value': 0,
            'created_by': cls.user.pk
        }

    def setUp(self):
        self.client.login(username="Testuser", password="123")

    def test_get_asset_create_view(self):
        resp = self.client.get(reverse('accounting:asset-create'))
        self.assertEqual(resp.status_code, 200)

    def test_post_asset_create_view(self):
        resp = self.client.post(reverse('accounting:asset-create'), data=self.data)
        self.assertEqual(resp.status_code, 302)

    def test_get_asset_update_view(self):
        resp = self.client.get(reverse('accounting:asset-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_asset_update_view(self):
        resp = self.client.post(reverse('accounting:asset-update',
            kwargs={'pk': 1}),data=self.data)
        self.assertEqual(resp.status_code, 302)

    def test_get_asset_list(self):
        resp = self.client.get(reverse('accounting:asset-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_asset_detail(self):
        resp = self.client.get(reverse('accounting:asset-detail', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

class ExpesnseViewTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'journals.json', 'settings.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()


    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser('Testuser', 'test@gmail.com', '123')
        create_account_models(cls)
        cls.recurring = RecurringExpense.objects.create(
            cycle=7,
            expiration_date=datetime.date.today(),
            start_date=datetime.date.today(),
            description = 'Test Description',
            category=0,
            amount=100,
            debit_account=cls.account_d
        )
    

    def setUp(self):
        self.client.login(username="Testuser", password='123')

    
    def test_get_expense_create_view(self):
        resp = self.client.get(reverse('accounting:expense-create'))
        self.assertEqual(resp.status_code, 200)

    def test_post_expense_create_view(self):
        resp = self.client.post(reverse('accounting:expense-create'), data={
            'description': 'description',
            'date': datetime.date.today(),
            'category': 1,
            'amount': 10,
            'debit_account': 1000,
            'recorded_by': self.user.pk
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_expense_list_view(self):
        resp = self.client.get(reverse('accounting:expense-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_expense_detail_view(self):
        resp = self.client.get(reverse('accounting:expense-detail', kwargs={
            'pk': self.expense.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_expense_delete_view(self):
        resp = self.client.get(reverse('accounting:expense-delete', kwargs={
            'pk': self.expense.pk
        }))
        self.assertEqual(resp.status_code, 200)
    
    def test_post_expense_delete_view(self):

        exp = Expense.objects.create(
            date=datetime.date.today(),
            description = 'Test Description',
            category=0,
            amount=100,
            billable=False,
            debit_account=self.account_d
        )
        resp = self.client.post(reverse('accounting:expense-delete', kwargs={
            'pk': exp.pk
        }))
        self.assertEqual(resp.status_code, 302)

    def test_get_recurring_expense_create_view(self):
        resp = self.client.get(reverse('accounting:recurring-expense-create'))
        self.assertEqual(resp.status_code, 200)

    def test_post_recurring_expense_create_view(self):
        resp = self.client.post(reverse('accounting:recurring-expense-create'), data={
            'description': 'description',
            'start_date': datetime.date.today(),
            'expiration_date': datetime.date.today(),
            'category': 1,
            'cycle':1,
            'amount': 10,
            'debit_account': 1000,
            'recorded_by': self.user.pk
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_recurring_expense_update_view(self):
        resp = self.client.get(reverse('accounting:recurring-expense-update', kwargs={
            'pk': self.recurring.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_recurring_expense_update_view(self):
        resp = self.client.post(reverse('accounting:recurring-expense-update', 
            kwargs={
            'pk': self.recurring.pk
        }), data={
            'description': 'description',
            'start_date': datetime.date.today(),
            'expiration_date': datetime.date.today(),
            'category': 1,
            'cycle':1,
            'amount': 10,
            'debit_account': 1000,
            'recorded_by': self.user.pk
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_recurring_expense_list_view(self):
        resp = self.client.get(reverse('accounting:recurring-expense-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_recurring_expense_detail_view(self):
        resp = self.client.get(reverse('accounting:recurring-expense-detail', kwargs={
            'pk': self.recurring.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_get_recurring_expense_delete_view(self):

        resp = self.client.get(reverse('accounting:expense-delete', kwargs={
            'pk': self.expense.pk
        }))
        self.assertEqual(resp.status_code, 200)
    
    def test_post_recurring_expense_delete_view(self):

        exp = RecurringExpense.objects.create(
            cycle=7,
            expiration_date=datetime.date.today(),
            start_date=datetime.date.today(),
            description = 'Test Description',
            category=0,
            amount=100,
            debit_account=self.account_d
        )
        resp = self.client.post(reverse('accounting:recurring-expense-delete', kwargs={
            'pk': exp.pk
        }))
        self.assertEqual(resp.status_code, 302)
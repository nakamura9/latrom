import datetime
import json
import urllib

from django.test import Client, TestCase
from django.test.client import RequestFactory
from django.urls import reverse

from django.contrib.auth.models import User
from accounting.models import Account, Expense, Currency
from common_data.tests import create_account_models, create_test_user
from employees.models import Employee
from invoicing.models import *
from latrom import settings
from services.models import Service, ServiceCategory
from .model_util import InvoicingModelCreator
import accounting
from invoicing.views import (CustomerStatementPDFView, 
                             SalesReportPDFView,
                             CustomerPaymentsPDFView,
                             SalesByCustomerReportPDFView,
                             AverageDaysToPayPDFView,
                             AccountsReceivableReportPDFView,
                             InvoiceAgingPDFView)
from common_data.tests import create_test_common_entities
import copy
from messaging.models import UserProfile

TODAY = datetime.datetime.today()


class CommonViewsTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'invoicing.json' ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        create_test_common_entities(cls)
        cls.client=Client()

    
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_home_page(self):
        resp = self.client.get(reverse('invoicing:home'))
        self.assertEqual(resp.status_code, 302)
        #after configuration
        settings = SalesConfig.objects.first()
        settings.is_configured = True
        settings.save()
        resp = self.client.get(reverse('invoicing:home'))
        self.assertEqual(resp.status_code, 200)
        settings.is_configured = False
        settings.save()

    def test_get_config_page(self):
        resp = self.client.get(reverse('invoicing:config', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_config_page(self):
        Currency.objects.create(name="test", symbol="t")
        resp = self.client.post(reverse('invoicing:config', 
            kwargs={'pk': 1}),
            data={
                "default_invoice_comments": "Test Comments",
                "document_theme": 1,
                "logo": "img.jpg",
                "business_name": 'test name',
                "next_invoice_number": 1,
                "next_quotation_number": 1,
                "currency": 1

            })
        self.assertEqual(resp.status_code, 302)

    def test_get_API_config_data(self):
        resp = self.client.get(reverse('invoicing:api-config', kwargs={
            'pk':1
        }))
        self.assertIsInstance(json.loads(resp.content), dict)


class ReportViewsTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'invoicing.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        cls.client=Client()

    @classmethod
    def setUpTestData(cls):
        imc = InvoicingModelCreator(cls)
        imc.create_all()
        create_test_common_entities(cls)

    
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_customer_statement_form_page(self):
        resp = self.client.get(reverse('invoicing:customer-statement-form'))
        self.assertEqual(resp.status_code, 200)

    def test_get_customer_statement_page(self):
        resp = self.client.get(reverse('invoicing:customer-statement'), data={
            'customer': 1,
            'default_periods': 0,
            'start_period': (TODAY - datetime.timedelta(days=30)).strftime(
                  '%m/%d/%Y'),
            'end_period': TODAY.strftime('%m/%d/%Y'),
        })
        self.assertEqual(resp.status_code, 200)

    def test_customer_statement_pdf(self):
        kwargs={
                 'start': (datetime.date.today() \
                             - datetime.timedelta(365)).strftime('%d %B %Y'),
                 'end': datetime.date.today().strftime('%d %B %Y'),
                 'customer': 1
             }
        req = RequestFactory().get(reverse('invoicing:customer-statement-pdf',
             kwargs=kwargs))
        resp = CustomerStatementPDFView.as_view()(req, **kwargs)
        self.assertEqual(resp.status_code, 200)

    def test_get_invoice_aging_report_page(self):
        resp = self.client.get(reverse('invoicing:invoice-aging'))
        self.assertEqual(resp.status_code, 200)

    def test_get_invoice_aging_report_pdf_page(self):
        req = RequestFactory().get(reverse('invoicing:invoice-aging-pdf'))
        resp = InvoiceAgingPDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_get_accounts_receivable_page(self):
        resp = self.client.get(reverse('invoicing:accounts-receivable-report'))
        self.assertEqual(resp.status_code, 200)
    
    def test_get_accounts_receivable_report_pdf_page(self):
        req = RequestFactory().get(reverse(
            'invoicing:accounts-receivable-report-pdf'))
        resp = AccountsReceivableReportPDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_get_average_days_to_pay(self):
        resp = self.client.get(reverse('invoicing:average-days-to-pay-report'))
        self.assertEqual(resp.status_code, 200)
    
    def test_get_average_days_to_pay_pdf_page(self):
        req = RequestFactory().get(reverse(
            'invoicing:average-days-to-pay-pdf'))
        resp = AverageDaysToPayPDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_get_sales_report_form_page(self):
        resp = self.client.get(reverse('invoicing:sales-report-form'))
        self.assertEqual(resp.status_code, 200)

    def test_get_sales_report_page(self):
        resp = self.client.get(reverse('invoicing:sales-report'), data={
            'default_periods': 4,
        })
        self.assertEqual(resp.status_code, 200)

    def test_sales_report_pdf(self):
        kwargs = {
                 'start': (datetime.date.today() \
                             - datetime.timedelta(365)).strftime('%d %B %Y'),
                 'end': datetime.date.today().strftime('%d %B %Y'),
             }
        req = RequestFactory().get(reverse('invoicing:sales-report-pdf',
             kwargs=kwargs))
        resp = SalesReportPDFView.as_view()(req, **kwargs)
        self.assertEqual(resp.status_code, 200)
    
    def test_sales_by_customer_form(self):
        resp = self.client.get(reverse('invoicing:sales-by-customer-form'))
        self.assertEqual(resp.status_code, 200)

    def test_sales_by_customer_report(self):
        resp = self.client.get(reverse(
            'invoicing:sales-by-customer-report'), data={
                'start_period': datetime.date.today() - datetime.timedelta(days=365),
                'end_period': datetime.date.today()
            })
        self.assertEqual(resp.status_code, 200)

    def test_sales_by_customer_pdf(self):
        kwargs = {
                'start': (datetime.date.today() \
                    - datetime.timedelta(days=365)).strftime('%d %B %Y'),
                'end': datetime.date.today().strftime('%d %B %Y')
            }
        req = RequestFactory().get(reverse(
            'invoicing:sales-by-customer-pdf', kwargs=kwargs))
        resp = SalesByCustomerReportPDFView.as_view()(req, **kwargs)
        
        self.assertEqual(resp.status_code, 200)

    def test_customer_payments_form(self):
        resp = self.client.get(reverse('invoicing:customer-payments-form'))
        self.assertEqual(resp.status_code, 200)

    def test_customer_payments_report(self):
        resp = self.client.get(reverse(
            'invoicing:customer-payments-report'), data={
                'start_period': (datetime.date.today() \
                    - datetime.timedelta(days=365)),
                'end_period': datetime.date.today()
            })
        self.assertEqual(resp.status_code, 200)

    def test_customer_payments_pdf(self):
        kwargs = {
                'start': (datetime.date.today() \
                    - datetime.timedelta(days=365)).strftime('%d %B %Y'),
                'end': datetime.date.today().strftime('%d %B %Y')
            }
        req = RequestFactory().get(reverse(
            'invoicing:customer-payments-pdf', kwargs=kwargs))
        resp = CustomerPaymentsPDFView.as_view()(req, **kwargs)
        
        self.assertEqual(resp.status_code, 200)


class CustomerViewsTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'invoicing.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        cls.client=Client()
        cls.CUSTOMER_DATA = {
            'name': 'Org',
            'billing_address': 'Test Address',
            'banking_details': 'Test Details',
            'customer_type': 'organization'
        }

    @classmethod
    def setUpTestData(cls):
        imc = InvoicingModelCreator(cls)
        imc.create_all()
        create_test_common_entities(cls)

    
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_customer_create_page(self):
        resp = self.client.get(reverse('invoicing:create-customer'))
        self.assertEqual(resp.status_code, 200)

    def test_post_customer_create_page_individual(self):
        new_data = copy.deepcopy(self.CUSTOMER_DATA)
        new_data.update({
                    'name': 'cust omer',
                    'customer_type': 'individual'
                })
        resp = self.client.post(
            reverse('invoicing:create-customer'),
                data=new_data)
        self.assertEqual(resp.status_code, 302)



    def test_post_customer_create_page(self):
        resp = self.client.post(
            reverse('invoicing:create-customer'),
                data=self.CUSTOMER_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_update_customer_page(self):
        resp = self.client.get(
            reverse('invoicing:update-customer',
                kwargs={
                'pk': 1
            })
        )
        self.assertEqual(resp.status_code, 200)
    
    def test_post_update_customer_page(self):
        resp = self.client.post(
            reverse('invoicing:update-customer',
                kwargs={
                'pk': self.customer_org.pk
            }), data=self.CUSTOMER_DATA,
        )
        self.assertEqual(resp.status_code, 302)

    def test_post_customer_update_page_switch_to_org(self):
        resp = self.client.post(
            reverse('invoicing:update-customer',
                kwargs={
                'pk': self.customer_ind.pk
            }), data=self.CUSTOMER_DATA,
        )
        self.assertEqual(resp.status_code, 302)

        #create ind customer again
        InvoicingModelCreator(self).create_customer_ind()

    def test_post_customer_update_page_switch_to_ind(self):
        new_data = copy.deepcopy(self.CUSTOMER_DATA)
        new_data.update({
                    'name': 'cust omer',
                    'customer_type': 'individual'
                })
        resp = self.client.post(
            reverse('invoicing:update-customer',
                kwargs={
                'pk': self.customer_org.pk
            }), data=new_data,
        )
        self.assertEqual(resp.status_code, 302)
        #revert
        InvoicingModelCreator(self).create_customer_org()


    def test_get_delete_customer_page(self):
        resp = self.client.get(reverse('invoicing:delete-customer', 
            kwargs={
                'pk': 1
            }))
        self.assertEqual(resp.status_code, 200)

    def test_post_customer_delete_page(self):
        cus = Customer.objects.create(
            organization=self.organization,
            billing_address="Test address",
            banking_details="test details"
        )
        resp = self.client.post(reverse('invoicing:delete-customer', 
            kwargs={'pk': cus.pk}))
        self.assertEqual(resp.status_code, 302)

    def test_get_customer_list_page(self):
        resp = self.client.get(reverse('invoicing:customers-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_customer_detail_page(self):
        resp = self.client.get(reverse('invoicing:customer-details', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)


class SalesRepViewsTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'employees.json', 
        'invoicing.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        imc = InvoicingModelCreator(cls)
        imc.create_all()
        cls.client=Client()
        cls.REP_DATA = {
            'employee': 1,
            'can_reverse_invoices': True,
            'can_offer_discounts': True
        }

    @classmethod
    def setUpTestData(cls):
        Employee.objects.create(
            first_name="Test",
            last_name="Employee",
        )
        create_test_user(cls)
        create_test_common_entities(cls)

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_create_sales_rep_page(self):
        resp = self.client.get(reverse('invoicing:create-sales-rep'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_sales_rep_page(self):
        resp = self.client.post(reverse('invoicing:create-sales-rep'),
            data=self.REP_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_update_sales_rep_page(self):
        resp = self.client.get(reverse('invoicing:update-sales-rep', kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_update_sales_rep_page(self):
        resp = self.client.post(reverse('invoicing:update-sales-rep', kwargs={'pk':1}), data=self.REP_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_delete_sales_rep_page(self):
        resp = self.client.get(reverse('invoicing:delete-sales-rep', kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)


    def test_post_delete_sales_rep_page(self):
        
        resp = self.client.post(reverse('invoicing:delete-sales-rep', kwargs={'pk':SalesRepresentative.objects.first().pk}))

        self.assertEqual(resp.status_code, 302)
        InvoicingModelCreator(self).create_sales_representative()
        

class InvoiceViewTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'journals.json','invoicing.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.DATA = {
            'status': 'invoice',
            'invoice_number': 10,
            'customer': cls.customer_org.pk,
            'salesperson': 1,
            'due': TODAY.strftime('%m/%d/%Y'),
            'date': TODAY.strftime('%m/%d/%Y'),
            'ship_from': 1,
            'terms': 'Test Terms',
            'comments': 'test comments',
            'item_list': json.dumps([
                {   
                    'type': 'product',
                    'selected': '1 - item',
                    'quantity': 1,
                    'tax': '1 - Tax',
                    'unitPrice': '5.00',
                    'discount': '0'
                },
                {   
                    'type': 'service',
                    'selected': '1 - item',
                    'hours': 1,
                    'fee': '200',
                    'tax': '1 - tax',
                    'discount': '0',
                    'rate': 50
                },
                {   
                    'type': 'expense',
                    'selected': '1 - item',
                    'tax': '1 - tax',
                    'discount': '0'
                }
                ])
        }

    @classmethod
    def setUpTestData(cls):
        imc = InvoicingModelCreator(cls)
        imc.create_all()
        create_test_user(cls)
        amc = accounting.tests.model_util.AccountingModelCreator(cls).create_tax()
        create_test_common_entities(cls)
        UserProfile.objects.create(
            user=User.objects.get(username='Testuser'),
            email_address="test@address.com",
            email_password='123',
        )

            
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_create_invoice_page(self):
        resp = self.client.get(reverse('invoicing:create-invoice'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_invoice_page(self):
        resp = self.client.post(reverse('invoicing:create-invoice'),
            data=self.DATA)
        self.assertEqual(resp.status_code, 302)

    
    def test_get_invoice_detail_page(self):
        resp = self.client.get(reverse('invoicing:invoice-detail',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)
    
    def test_get_invoice_update_page(self):
        resp = self.client.get(reverse('invoicing:invoice-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_invoice_update_page(self):
        simple_data = dict(self.DATA)
        resp = self.client.post(reverse('invoicing:invoice-update',
            kwargs={'pk': 1}),
                data=simple_data)
        
        self.assertEqual(resp.status_code, 302)


    def test_post_invoice_update_page_as_draft(self):
        simple_data = dict(self.DATA)
        inv = Invoice.objects.first()
        inv.draft=True
        inv.save()
        resp = self.client.post(reverse('invoicing:invoice-update',
            kwargs={'pk': 1}),
                data=simple_data)
        
        
        self.assertEqual(resp.status_code, 302)
    
    def test_get_invoice_list_page(self):
        resp = self.client.get(reverse('invoicing:invoice-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_comnbined_invoice_payment_page(self):
        resp = self.client.get(reverse('invoicing:invoice-payment', 
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_invoice_payment_page(self):
        resp = self.client.post(reverse('invoicing:invoice-payment',
            kwargs={'pk': 1}), data={
                'invoice': 1,
                'amount': 10,
                'method': 'transfer',
                'sales_rep': 1,
                'comments': 'Test Comments',
                'date': TODAY.strftime('%m/%d/%Y')
            })
        self.assertEqual(resp.status_code, 302)
    
    def test_get_invoice_payment_detail_page(self):
        resp = self.client.get(reverse('invoicing:invoice-payment-detail', 
            kwargs={'pk': self.payment.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_invoice_pdf_page(self):
        #assume that the detail view can be converted to a pdf 
        resp = self.client.get(reverse('invoicing:invoice-detail',
            kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_invoice_email_page(self):
        with self.assertRaises(Exception):
            resp = self.client.get(reverse('invoicing:invoice-email',
                kwargs={'pk':1})) 
        

    def test_post_invoice_email_page(self):
        with self.assertRaises(Exception):
            self.client.post(reverse('invoicing:invoice-email',
            kwargs={'pk':1}), data={
                'recipient': 'kandoroc@gmail.com',
                'subject': 'Test Subject',
                'content': 'TestContent'
            })

    def test_get_invoice_returns_page(self):
        resp = self.client.get(reverse('invoicing:invoice-returns',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_credit_note_create_page(self):
        resp = self.client.get(reverse('invoicing:credit-note-create',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_credit_note_create_page(self):
        resp = self.client.post(reverse('invoicing:credit-note-create',
            kwargs={'pk': 1}), data={
                'date': TODAY.strftime('%m/%d/%Y'),
                'invoice': 1,
                'comments': 'test comments',
                'returned-items': json.dumps([{
                    'product': '1 - product',
                    'returned_quantity': 1    
                }])
            })
        
        self.assertEqual(resp.status_code, 302)

    def test_get_credit_note_detail_page(self):
        resp = self.client.get(reverse('invoicing:credit-note-detail',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_credit_note_list_page(self):
        resp = self.client.get(reverse('invoicing:credit-note-list'))
        self.assertEqual(resp.status_code, 200)

    
    def test_verify_invoice(self):
        from django.contrib.auth.models import User
        resp = self.client.post('/invoicing/invoice/verify/' + \
                str(self.invoice.pk),
            data={
                'user': '1',
                'password': '123'
            })
        self.assertEqual(resp.status_code, 302)
    
    def test_verify_quotation(self):
        from django.contrib.auth.models import User
        resp = self.client.post('/invoicing/invoice/verify/' + \
            str(self.quotation.pk),
            data={
                'user': User.objects.first().pk,
                'password': '123'
            })
        self.assertEqual(resp.status_code, 302)

    
    def test_get_sales_invoice_expense_page(self):
        resp = self.client.get("/invoicing/invoice/shipping-costs/1")
        self.assertEqual(resp.status_code, 200)

    def test_post_sales_invoice_expense_page(self):
        resp = self.client.post("/invoicing/invoice/shipping-costs/1", data={
            'amount': 10,
            'description': 'description',
            'recorded_by': 1,
            'date': datetime.date.today(),
            'reference': 'ref'
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_shipping_expense_list(self):
        resp = self.client.get('/invoicing/invoice/shipping-costs/list/1')
        self.assertEqual(resp.status_code, 200)


class QuotationViewTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'journals.json','invoicing.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.DATA = {
            'status': 'quotation',
            'customer': cls.customer_org.pk,
            'salesperson': 1,
            'quotation_valid': TODAY.strftime('%m/%d/%Y'),
            'quotation_date': TODAY.strftime('%m/%d/%Y'),
            'ship_from': 1,
            'terms': 'Test Terms',
            'comments': 'test comments',
            'item_list': json.dumps([
                {   
                    'type': 'product',
                    'selected': '1 - item',
                    'unitPrice': '5.00',
                    'quantity': 1,
                    'tax': '1 - Tax',
                    'discount': '0'
                },
                {   
                    'type': 'service',
                    'selected': '1 - item',
                    'hours': 1,
                    'tax': '1 - tax',
                    'discount': '0',
                    'fee': 200,
                    'rate': 20.00
                },
                {   
                    'type': 'expense',
                    'selected': '1 - item',
                    'tax': '1 - tax',
                    'discount': '0'
                }
                ])
        }

    @classmethod
    def setUpTestData(cls):
        imc = InvoicingModelCreator(cls)
        imc.create_all()
        create_test_user(cls)
        amc = accounting.tests.model_util.AccountingModelCreator(cls).create_tax()
        create_test_common_entities(cls)

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_quotation_create_view(self):
        resp = self.client.get(reverse('invoicing:create-quotation'))

        self.assertEqual(resp.status_code, 200)

    def test_get_quotation_create_view_with_customer(self):
        resp = self.client.get(reverse('invoicing:create-quotation', kwargs={
            'customer': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_quotation_create_view(self):
        resp = self.client.post(reverse('invoicing:create-quotation'), 
            data=self.DATA)
        
        self.assertEqual(resp.status_code, 302)

    def test_get_quotation_update_view(self):
        resp = self.client.get(reverse('invoicing:quotation-update', kwargs={
            'pk': self.quotation.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_quotation_update_view(self):
        self.quotation.draft=True
        self.quotation.save()
        resp = self.client.post(reverse('invoicing:quotation-update', kwargs={
            'pk': self.quotation.pk
        }), data=self.DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_quotation_detail_view(self):
        resp = self.client.get(reverse('invoicing:quotation-details', kwargs={
            'pk': 1
        }))
        self.assertEqual(resp.status_code, 200)

    def test_make_invoice_from_quotation(self):
        resp = self.client.get(reverse('invoicing:make-invoice', kwargs={
            'pk': self.quotation.pk
        }))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Invoice.objects.get(pk=self.quotation.pk).status,     "invoice")

        self.quotation.status = "quotation"
        self.quotation.save()


    def test_make_proforma_from_quotation(self):
        resp = self.client.get(reverse('invoicing:make-proforma', kwargs={
            'pk': self.quotation.pk
        }))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Invoice.objects.get(pk=self.quotation.pk).status,    "proforma")

        self.quotation.status = "quotation"
        self.quotation.save()


class ConfigWizardTests(TestCase):
    fixtures = ['common.json', 'invoicing.json', 'accounts.json', 'journals.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import User

        cls.user = User.objects.create_superuser(username="Testuser", email="admin@test.com", password="123")

    def setUp(self):
        self.client.login(username='Testuser', password='123')
    

    def test_config_wizard(self):
        config_data = {
            'config_wizard-current_step': 0,
            '0-next_invoice_number': 10,
            '0-next_quotation_number': 10
        }

        customer_data = {
            'config_wizard-current_step': 1,
            '1-customer_type': 'individual',
            '1-name': 'some one'
        }

        employee_data = {
            '2-first_name': 'first',
            '2-last_name': 'last',
            '2-leave_days': 1,
            '2-pin': 1000,
            'config_wizard-current_step': 2,
        }

        rep_data = {
            'config_wizard-current_step': 3,
            '3-employee': 1
        }

        data_list = [config_data, customer_data, employee_data, rep_data]

        for step, data in enumerate(data_list, 1):

            try:
                resp = self.client.post(reverse('invoicing:config-wizard'), 
                    data=data)

                if step == len(data_list):
                    #print(resp.context['form'].errors)                    
                    self.assertEqual(resp.status_code, 302)
                else:
                    self.assertEqual(resp.status_code, 200)
                    if resp.context.get('form'):
                        if hasattr(resp.context['form'], 'errors'):
                            print(resp.context['form'].errors)
            except ValueError:
                pass
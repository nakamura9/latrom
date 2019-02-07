import datetime
import json
import urllib

from django.test import Client, TestCase
from django.urls import reverse

from accounting.models import Account, Expense, Currency
from common_data.tests import create_account_models, create_test_user
from employees.models import Employee
from invoicing.models import *
from invoicing.tests.models import create_test_invoicing_models
from latrom import settings
from inventory.tests import create_test_inventory_models
from services.models import Service, ServiceCategory

TODAY = datetime.datetime.today()
settings.TEST_RUN_MODE = True

class CommonViewsTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'invoicing.json' ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        cls.client=Client()

    
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_home_page(self):
        resp = self.client.get(reverse('invoicing:home'))
        self.assertEqual(resp.status_code, 200)


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
        create_test_invoicing_models(cls)

        cls.client=Client()

    
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

    def test_get_invoice_aging_report_page(self):
        resp = self.client.get(reverse('invoicing:invoice-aging'))
        self.assertEqual(resp.status_code, 200)

    def test_get_sales_report_form_page(self):
        resp = self.client.get(reverse('invoicing:sales-report-form'))
        self.assertEqual(resp.status_code, 200)

    def test_get_sales_report_page(self):
        resp = self.client.get(reverse('invoicing:sales-report'), data={
            'default_periods': 4,
        })
        self.assertEqual(resp.status_code, 200)

class CustomerViewsTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'invoicing.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        create_test_invoicing_models(cls)
        cls.client=Client()
        cls.CUSTOMER_DATA = {
            'organizaiton': 1,
            'billing_address': 'Test Address',
            'banking_details': 'Test Details'
        }

    
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_customer_create_page(self):
        resp = self.client.get(reverse('invoicing:create-organization-customer'))
        self.assertEqual(resp.status_code, 200)

    def test_post_customer_create_page(self):
        resp = self.client.post(
            reverse('invoicing:create-organization-customer'),
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
                'pk': 1
            }), data=self.CUSTOMER_DATA,
        )
        self.assertEqual(resp.status_code, 302)

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
        resp = self.client.get(reverse('invoicing:organization-customers-list'))
        self.assertEqual(resp.status_code, 200)


class SalesRepViewsTests(TestCase):
    fixtures = ['common.json', 'accounts.json', 'employees.json', 
        'invoicing.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.REP_DATA = {
            'employee': 2,
            'can_reverse_invoices': True,
            'can_offer_discounts': True
        }

    @classmethod
    def setUpTestData(cls):
        Employee.objects.create(
            first_name="Test",
            last_name="Employee",
            hire_date=TODAY
        )
        create_test_user(cls)
        create_test_invoicing_models(cls)

    
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
        obj = SalesRepresentative.objects.create(
            employee= Employee.objects.get(pk=2)
        )
        resp = self.client.post(reverse('invoicing:delete-sales-rep', kwargs={'pk':2}))

        self.assertEqual(resp.status_code, 302)
        obj.hard_delete()


class BillViewTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'journals.json', 'invoicing.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.BILL_DATA = {
            'customer_reference': 'ref',
            'status': 'invoice',
            'customer': cls.customer_org.pk,
            'salesperson': 1,
            'due': TODAY.strftime('%m/%d/%Y'),
            'date': TODAY.strftime('%m/%d/%Y'),
            'discount': 0,
            'terms': 'Test Terms',
            'comments': 'test comments',
            'item_list': urllib.parse.quote(json.dumps([{'pk':1}]))
        }

    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)
        create_test_invoicing_models(cls)
        cls.exp = Expense.objects.create(
            date=TODAY,
            billable=True,
            customer=cls.customer_org,
            amount=10,
            description="test description",
            category=0,
            debit_account=Account.objects.first()
        )
        cls.bill = Bill.objects.create(
            customer_reference="100",
            status='invoice',
            customer=cls.customer_org,
        )
        cls.line = BillLine.objects.create(
            bill=cls.bill,
            expense=cls.exp
            )

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_create_bill_page(self):
        resp = self.client.get(reverse('invoicing:bill-create'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_bill_page(self):
        resp = self.client.post(reverse('invoicing:bill-create'),
            data=self.BILL_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_bill_detail_page(self):
        resp = self.client.get(reverse('invoicing:bill-details',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_bill_draft_update_page(self):
        resp = self.client.get(reverse('invoicing:bill-draft-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_bill_draft_update_page(self):
        resp = self.client.post(reverse('invoicing:bill-draft-update',
            kwargs={'pk': 1}), data=self.BILL_DATA)
       
        self.assertEqual(resp.status_code, 302)

    def test_get_bill_update_page(self):
        resp = self.client.get(reverse('invoicing:bill-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_bill_update_page(self):
        simple_data = dict(self.BILL_DATA)
        del simple_data['discount']
        del simple_data['item_list']
        resp = self.client.post(reverse('invoicing:bill-update',
            kwargs={'pk': 1}),
                data=simple_data)

        self.assertEqual(resp.status_code, 302)
    
    def test_get_bill_list_page(self):
        resp = self.client.get(reverse('invoicing:bill-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_bill_payment_page(self):
        resp = self.client.get(reverse('invoicing:bill-payment', 
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_bill_payment_page(self):
        resp = self.client.post(reverse('invoicing:bill-payment',
            kwargs={'pk': 1}), data={
                'bill': 1,
                'payment_for': 2,
                'amount': 10,
                'method': 'transfer',
                'sales_rep': 1,
                'comments': 'Test Comments',
                'date': TODAY.strftime('%m/%d/%Y')
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_bill_payment_detail_page(self):
        obj = Payment.objects.create(
            bill=self.bill,
            payment_for=2,
            amount=10,
            method='transfer',
            sales_rep=SalesRepresentative.objects.first(),
            date=TODAY,
        )
        resp = self.client.get(reverse('invoicing:bill-payment-detail', 
            kwargs={'pk': obj.pk}))
        self.assertEqual(resp.status_code, 200)
        obj.delete()

    def test_bill_pdf_page(self):
        #assume that the detail view can be converted to a pdf 
        resp = self.client.get(reverse('invoicing:bill-detail',
            kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_bill_email_page(self):
        resp = self.client.get(reverse('invoicing:bill-email',
            kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_bill_email_page(self):
        with self.assertRaises(Exception):
            self.client.post(reverse('invoicing:bill-email',
            kwargs={'pk':1}), data={
                'recipient': 'kandoroc@gmail.com',
                'subject': 'Test Subject',
                'content': 'TestContent'
            })


class CombinedInvoiceViewTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'journals.json','invoicing.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.COMBINED_DATA = {
            'status': 'invoice',
            'customer': cls.customer_org.pk,
            'salesperson': 1,
            'due': TODAY.strftime('%m/%d/%Y'),
            'date': TODAY.strftime('%m/%d/%Y'),
            'discount': 0,
            'terms': 'Test Terms',
            'comments': 'test comments',
            'item_list': json.dumps([
                {   'lineType': 'sale',
                    'data': {
                        'item': '1 - item',
                        'quantity': 1
                    }},
                    {   'lineType': 'service',
                    'data': {
                        'service': '1 - item',
                        'hours': 1
                    }},
                    {   'lineType': 'billable',
                    'data': {
                        'billable': '1 - item'
                    }}
                ])
        }

    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)
        create_test_inventory_models(cls)
        create_test_invoicing_models(cls)
        cls.exp = Expense.objects.create(
            date=TODAY,
            billable=True,
            customer=cls.customer_org,
            amount=10,
            description="test description",
            category=0,
            debit_account=Account.objects.first()
        )
        cls.inv = CombinedInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
        )
        cat = ServiceCategory.objects.create(
            name="name"
        )
        
        cls.service = Service.objects.create(
            name="Test Service",
            description="some description",
            flat_fee=10,
            hourly_rate=1,
            frequency="once",
            category=cat
        )
        cls.line_sale = CombinedInvoiceLine.objects.create(
            invoice=cls.inv,
            product=cls.product,
            line_type=1,
            quantity_or_hours=1
        )
        cls.line_service = CombinedInvoiceLine.objects.create(
            invoice=cls.inv,
            service=cls.service,
            line_type=2,
            quantity_or_hours=0
        )
        cls.line_bill = CombinedInvoiceLine.objects.create(
            invoice=cls.inv,
            expense=cls.exp,
            line_type=3,
            quantity_or_hours=0
        )
        
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_create_combined_invoice_page(self):
        resp = self.client.get(reverse('invoicing:create-combined-invoice'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_combined_invoice_page(self):
        resp = self.client.post(reverse('invoicing:create-combined-invoice'),
            data=self.COMBINED_DATA)
        self.assertEqual(resp.status_code, 302)

    
    def test_get_combined_invoice_detail_page(self):
        resp = self.client.get(reverse('invoicing:combined-invoice-detail',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_combinend_invoice_draft_update_page(self):
        resp = self.client.get(reverse('invoicing:combined-draft-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_combined_invoice_draft_update_page(self):
        resp = self.client.post(reverse('invoicing:combined-draft-update',
            kwargs={'pk': 1}), data=self.COMBINED_DATA)
       
        self.assertEqual(resp.status_code, 302)
    
    def test_get_combined_invoice_update_page(self):
        resp = self.client.get(reverse('invoicing:combined-invoice-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_combined_invoice_update_page(self):
        simple_data = dict(self.COMBINED_DATA)
        del simple_data['discount']
        del simple_data['item_list']
        resp = self.client.post(reverse('invoicing:combined-invoice-update',
            kwargs={'pk': 1}),
                data=simple_data)
        self.assertEqual(resp.status_code, 302)
    
    def test_get_combined_invoice_list_page(self):
        resp = self.client.get(reverse('invoicing:combined-invoice-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_comnbined_invoice_payment_page(self):
        resp = self.client.get(reverse('invoicing:combined-invoice-payment', 
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_combined_invoice_payment_page(self):
        resp = self.client.post(reverse('invoicing:combined-invoice-payment',
            kwargs={'pk': 1}), data={
                'combined_invoice': 1,
                'payment_for': 3,
                'amount': 10,
                'method': 'transfer',
                'sales_rep': 1,
                'comments': 'Test Comments',
                'date': TODAY.strftime('%m/%d/%Y')
            })
        self.assertEqual(resp.status_code, 302)
    
    def test_get_combined_invoice_payment_detail_page(self):
        obj = Payment.objects.create(
            combined_invoice=self.inv,
            payment_for=3,
            amount=10,
            method='transfer',
            sales_rep=SalesRepresentative.objects.first(),
            date=TODAY,
        )
        resp = self.client.get(reverse('invoicing:combined-invoice-payment-detail', 
            kwargs={'pk': obj.pk}))
        self.assertEqual(resp.status_code, 200)
        obj.delete()

    def test_combined_invoice_pdf_page(self):
        #assume that the detail view can be converted to a pdf 
        resp = self.client.get(reverse('invoicing:combined-invoice-detail',
            kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_combined_invoice_email_page(self):
        resp = self.client.get(reverse('invoicing:combined-invoice-email',
            kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_combined_invoice_email_page(self):
        with self.assertRaises(Exception):
            self.client.post(reverse('invoicing:combined-invoice-email',
            kwargs={'pk':1}), data={
                'recipient': 'kandoroc@gmail.com',
                'subject': 'Test Subject',
                'content': 'TestContent'
            })


class SalesViewTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'journals.json', 'invoicing.json', 'inventory.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.SALE_DATA = {
            'purchase_order_number': 'ref',
            'ship_from': 1,
            'tax': 1,
            'status': 'invoice',
            'customer': cls.customer_org.pk,
            'salesperson': 1,
            'due': TODAY.strftime('%m/%d/%Y'),
            'date': TODAY.strftime('%m/%d/%Y'),
            'discount': 0,
            'terms': 'Test Terms',
            'comments': 'test comments',
            'item_list': json.dumps([
                {
                    'product': '1 - name',
                    'quantity': 1
                }
            ])
        }

    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)
        create_test_inventory_models(cls)
        create_test_invoicing_models(cls)
        
        cls.inv = SalesInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
        )
        cls.line = SalesInvoiceLine.objects.create(
            product=cls.product,
            quantity=1,
            invoice=cls.inv
            )
        cls.cr_note = CreditNote.objects.create(
            date=TODAY,
            invoice=cls.inv,
            comments="Test comment"
        )

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_create_sales_invoice_page(self):
        resp = self.client.get(reverse('invoicing:create-sales-invoice'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_sales_invoice_page(self):
        resp = self.client.post(reverse('invoicing:create-sales-invoice'),
            data=self.SALE_DATA)
        self.assertEqual(resp.status_code, 302)
    
    def test_get_sales_invoice_detail_page(self):
        resp = self.client.get(reverse('invoicing:sales-invoice-detail',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_sales_invoice_draft_update_page(self):
        resp = self.client.get(reverse('invoicing:sales-draft-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)
    
    def test_post_sales_invoice_draft_update_page(self):
        resp = self.client.post(reverse('invoicing:sales-draft-update',
            kwargs={'pk': 1}), data=self.SALE_DATA)
       
        self.assertEqual(resp.status_code, 302)

    def test_get_sale_update_page(self):
        resp = self.client.get(reverse('invoicing:sales-invoice-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_sales_update_page(self):
        simple_data = dict(self.SALE_DATA)
        del simple_data['discount']
        del simple_data['item_list']
        resp = self.client.post(reverse('invoicing:sales-invoice-update',
            kwargs={'pk': 1}),
                data=simple_data)
        self.assertEqual(resp.status_code, 302)
    
    def test_get_sale_list_page(self):
        resp = self.client.get(reverse('invoicing:sales-invoice-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_sale_payment_page(self):
        resp = self.client.get(reverse('invoicing:sales-invoice-payment', 
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_sale_payment_page(self):
        resp = self.client.post(reverse('invoicing:sales-invoice-payment',
            kwargs={'pk': 1}), data={
                'sales_invoice': 1,
                'payment_for': 0,
                'amount': 10,
                'method': 'transfer',
                'sales_rep': 1,
                'comments': 'Test Comments',
                'date': TODAY.strftime('%m/%d/%Y')
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_sale_payment_detail_page(self):
        obj = Payment.objects.create(
            sales_invoice=self.inv,
            payment_for=0,
            amount=10,
            method='transfer',
            sales_rep=SalesRepresentative.objects.first(),
            date=TODAY,
        )
        resp = self.client.get(reverse('invoicing:sales-invoice-payment-detail', 
            kwargs={'pk': obj.pk}))
        self.assertEqual(resp.status_code, 200)
        obj.delete()
    
    def test_sale_pdf_page(self):
        #assume that the detail view can be converted to a pdf 
        resp = self.client.get(reverse('invoicing:sales-invoice-detail',
            kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_sale_email_page(self):
        resp = self.client.get(reverse('invoicing:sales-invoice-email',
            kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_sale_email_page(self):
        with self.assertRaises(Exception):
            self.client.post(reverse('invoicing:sales-invoice-email',
            kwargs={'pk':1}), data={
                'recipient': 'kandoroc@gmail.com',
                'subject': 'Test Subject',
                'content': 'TestContent'
            })

    def test_get_sales_invoice_returns_page(self):
        resp = self.client.get(reverse('invoicing:sales-invoice-returns',
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

    def test_verify_sales_invoice(self):
        resp = self.client.get('/invoicing/sales-invoice/1/verify/quotation')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(SalesInvoice.objects.get(pk=1).status, "quotation")

    def test_get_sales_invoice_expense_page(self):
        resp = self.client.get("/invoicing/sales-invoice/shipping-costs/1")
        self.assertEqual(resp.status_code, 200)

    def test_post_sales_invoice_expense_page(self):
        resp = self.client.post("/invoicing/sales-invoice/shipping-costs/1", data={
            'amount': 10,
            'description': 'description',
            'recorded_by': 1,
            'date': datetime.date.today()
        })
        self.assertEqual(resp.status_code, 200)

    def test_get_shipping_expense_list(self):
        resp = self.client.get('/invoicing/sales-invoice/shipping-costs/list/1')
        self.assertEqual(resp.status_code, 200)


class ServiceInvoiceViewTests(TestCase):
    fixtures = ['common.json','accounts.json', 'employees.json', 
        'journals.json','invoicing.json']
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client=Client()
        cls.SERVICE_DATA = {
            'status': 'invoice',
            'tax': 1,
            'customer': cls.customer_org.pk,
            'salesperson': 1,
            'due': TODAY.strftime('%m/%d/%Y'),
            'date': TODAY.strftime('%m/%d/%Y'),
            'discount': 0,
            'terms': 'Test Terms',
            'comments': 'test comments',
            'item_list': json.dumps([
                {
                    'service': '1 - service',
                    'hours': '1'
                }
            ])
        }

    @classmethod
    def setUpTestData(cls):
        create_test_user(cls)
        create_test_inventory_models(cls)
        create_test_invoicing_models(cls)
        
        cls.inv = ServiceInvoice.objects.create(
            status='invoice',
            customer=cls.customer_org,
        )
        cat = ServiceCategory.objects.create(
            name="name"
        )
        cls.service = Service.objects.create(
            name="Test Service",
            description="some description",
            flat_fee=10,
            hourly_rate=1,
            frequency="once",
            category=cat
        )
        cls.line = ServiceInvoiceLine.objects.create(
            invoice=cls.inv,
            service=cls.service,
            hours=0
        )

    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_create_service_invoice_page(self):
        resp = self.client.get(reverse('invoicing:create-service-invoice'))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_service_invoice_page(self):
        resp = self.client.post(reverse('invoicing:create-service-invoice'),
            data=self.SERVICE_DATA)
        self.assertEqual(resp.status_code, 302)
    
    def test_get_service_invoice_detail_page(self):
        resp = self.client.get(reverse('invoicing:service-invoice-detail',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_service_invoice_draft_update_page(self):
        resp = self.client.get(reverse('invoicing:service-draft-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)
    
    def test_post_service_invoice_draft_update_page(self):
        resp = self.client.post(reverse('invoicing:service-draft-update',
            kwargs={'pk': 1}), data=self.SERVICE_DATA)
       
        self.assertEqual(resp.status_code, 302)
    
    def test_get_service_update_page(self):
        resp = self.client.get(reverse('invoicing:service-invoice-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_service_update_page(self):
        simple_data = dict(self.SERVICE_DATA)
        del simple_data['discount']
        del simple_data['item_list']
        resp = self.client.post(reverse('invoicing:service-invoice-update',
            kwargs={'pk': 1}),
                data=simple_data)
        
        self.assertEqual(resp.status_code, 302)
    
    def test_get_service_list_page(self):
        resp = self.client.get(reverse('invoicing:service-invoice-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_service_payment_page(self):
        resp = self.client.get(reverse('invoicing:service-invoice-payment', 
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_service_payment_page(self):
        resp = self.client.post(reverse('invoicing:service-invoice-payment',
            kwargs={'pk': 1}), data={
                'service_invoice': 1,
                'payment_for': 1,
                'amount': 10,
                'method': 'transfer',
                'sales_rep': 1,
                'comments': 'Test Comments',
                'date': TODAY.strftime('%m/%d/%Y')
            })
        self.assertEqual(resp.status_code, 302)
    
    def test_get_service_payment_detail_page(self):
        obj = Payment.objects.create(
            service_invoice=self.inv,
            payment_for=1,
            amount=10,
            method='transfer',
            sales_rep=SalesRepresentative.objects.first(),
            date=TODAY,
        )
        resp = self.client.get(
            reverse('invoicing:service-invoice-payment-detail', 
                kwargs={'pk': obj.pk}))
        self.assertEqual(resp.status_code, 200)
        obj.delete()
    
    def test_service_pdf_page(self):
        #assume that the detail view can be converted to a pdf 
        resp = self.client.get(reverse('invoicing:service-invoice-detail',
            kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_service_email_page(self):
        resp = self.client.get(reverse('invoicing:service-invoice-email',
            kwargs={'pk':1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_service_email_page(self):
        with self.assertRaises(Exception):
            self.client.post(reverse('invoicing:service-invoice-email',
            kwargs={'pk':1}), data={
                'recipient': 'kandoroc@gmail.com',
                'subject': 'Test Subject',
                'content': 'TestContent'
            })

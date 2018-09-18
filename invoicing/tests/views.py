from django.test import TestCase, Client
from latrom import settings
import datetime 
from django.urls import reverse
import json
from invoicing.models import *
from common_data.tests import create_test_user

TODAY = datetime.datetime.today()
settings.TEST_RUN_MODE = True
from invoicing.tests.models import create_test_invoicing_models

class CommonViewsTests(TestCase):
    fixtures = ['common.json', 'employees.json', 'invoicing.json',  ]

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
        resp = self.client.post(reverse('invoicing:config', 
            kwargs={'pk': 1}),
            data={
                "default_invoice_comments": "Test Comments",
                "document_theme": 1,
                "currency": "$",
                "logo": "img.jpg",
                "price_multiplier": 0.0,
                "business_name": 'test name'
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_API_config_data(self):
        resp = self.client.get(reverse('invoicing:api-config', kwargs={
            'pk':1
        }))
        self.assertIsInstance(json.loads(resp.content), dict)

class InvoiceViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        cls.client=Client()


    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    

class ReportViewsTests(TestCase):
    fixtures = ['common.json', 'employees.json', 'invoicing.json']

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

class CustomerViewsTests(TestCase):
    fixtures = ['common.json', 'employees.json', 'invoicing.json']

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
        resp = self.client.get(reverse('invoicing:create-customer'))
        self.assertEqual(resp.status_code, 200)

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
        resp = self.client.get(reverse('invoicing:customer-list'))
        self.assertEqual(resp.status_code, 200)

class SalesRepViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        create_test_user(cls)
        cls.client=Client()

    
    def setUp(self):
        #wont work in setUpClass
        self.client.login(username='Testuser', password='123')

    def test_get_create_customer_page(self):
        resp = self.client.get(reverse('invoicing:create-customer'))
        self.assertEqual(resp.status_code, 200)
    
    def test_post_create_customer_page(self):
        pass

        
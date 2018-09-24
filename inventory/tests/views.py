
import datetime
import json
import urllib

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounting.models import Account, JournalEntry
from common_data.models import Organization
from common_data.tests import create_account_models, create_test_user
from inventory import models

from .models import create_test_inventory_models

TODAY = datetime.date.today()
        

class ViewTests(TestCase):
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpClass(cls):
        super(ViewTests, cls).setUpClass()
        cls.client = Client

    @classmethod
    def setUpTestData(cls):
        super(ViewTests, cls).setUpTestData()
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)
        
        cls.PRODUCT_DATA = {
            'name' : 'Other Test Item',
            'unit' : cls.unit.pk,
            'margin' : 0.2,
            'markup' : 0.2,
            'direct_price' : 10,
            'pricing_method': 2,
            'unit_purchase_price' : 8,
            'description' : 'Test Description',
            'supplier' : cls.supplier.pk,
            'quantity' : 10,
            'minimum_order_level' : 0,
            'maximum_stock_level' : 20,
            'category' : cls.category.pk
        }
        cls.SUPPLIER_DATA = {
            'organization': cls.organization,
            'account': cls.account_c.pk
        }
        cls.ORDER_DATA = {
            'expected_receipt_date' : TODAY,
            'issue_date' : TODAY,
            'deferred_date' : TODAY,
            'supplier' : cls.supplier.pk,
            'bill_to' : 'Test Bill to',
            'ship_to' : cls.warehouse.pk,
            'type_of_order': 0,
            'tracking_number' : '34234',
            'notes' : 'Test Note',
            'status' : 'draft',
            'items[]': urllib..parse.quote(json.dumps({
                'name': cls.product.pk,
                'quantity': 10,
                'order_price': 10
                }))
        }


    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_home_page(self):
        resp = self.client.get(reverse('inventory:home'))
        self.assertTrue(resp.status_code == 200)

    #MISC

    def test_get_unit_form(self):
        resp = self.client.get(reverse('inventory:unit-create'))
        self.assertTrue(resp.status_code == 200)

    def test_get_category_form(self):
        resp = self.client.get(reverse('inventory:category-create'))
        self.assertTrue(resp.status_code == 200)

    #SUPPLIER

    def test_get_supplier_create(self):
        resp = self.client.get(reverse('inventory:supplier-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_supplier_create(self):
        resp = self.client.post(reverse('inventory:supplier-create'),
            data=self.SUPPLIER_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_supplier_list(self):
        resp = self.client.get(reverse('inventory:supplier-list'))
        self.assertTrue(resp.status_code == 200)

    def test_get_supplier_update(self):
        resp = self.client.get(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.supplier.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_supplier_update(self):
        resp = self.client.post(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.supplier.pk
            }), data=self.SUPPLIER_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_supplier_delete(self):
        resp = self.client.get(reverse('inventory:supplier-delete',
            kwargs={
                'pk': self.supplier.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_supplier_delete(self):
        resp = self.client.post(reverse('inventory:supplier-delete',
            kwargs={
                'pk': models.Supplier.objects.latest('pk').pk
            }))
        self.assertTrue(resp.status_code == 302)

    #ITEM

    def test_get_product_form(self):
        resp = self.client.get(reverse('inventory:product-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_product_form(self):
        resp = self.client.post(reverse('inventory:product-create'),
            data=self.PRODUCT_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_product_list(self):
        resp = self.client.get(reverse('inventory:product-list'))
        self.assertTrue(resp.status_code == 200)

    def test_get_product_update_form(self):
        resp = self.client.get(reverse('inventory:product-update',
            kwargs={
                'pk': self.product.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_product_update_form(self):
        resp = self.client.post(reverse('inventory:product-update',
            kwargs={
                'pk': self.product.pk
            }), data=self.PRODUCT_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_product_delete_form(self):
        resp = self.client.get(reverse('inventory:product-delete',
            kwargs={
                'pk': self.product.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_product_delete_form(self):
        resp = self.client.post(reverse('inventory:product-delete',
            kwargs={
                'pk': models.Product.objects.latest('pk').pk
            }))
        self.assertTrue(resp.status_code == 302)

    def test_get_product_detail(self):
        resp = self.client.get(reverse('inventory:product-detail',
            kwargs={
                'pk': self.product.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_get_quick_product_form(self):
        resp = self.client.get(reverse('inventory:quick-product'))
        self.assertTrue(resp.status_code == 200)

    #ORDER

    def test_get_order_form(self):
        resp = self.client.get(reverse('inventory:order-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_order_form(self):
        resp = self.client.post(reverse('inventory:order-create'), 
        data=self.ORDER_DATA)
        self.assertTrue(resp.status_code == 302)
        #tests the created transaction
        self.assertEqual(Account.objects.get(pk=1004).balance, 100)

    def test_get_order_list(self):
        resp = self.client.get(reverse('inventory:order-list'))
        self.assertTrue(resp.status_code == 200)

    def test_get_order_update_form(self):
        resp = self.client.get(reverse('inventory:order-update',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_order_update_form(self):
        resp = self.client.post(reverse('inventory:order-update',
            kwargs={
                'pk': self.order.pk
            }), data=self.ORDER_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_order_delete_form(self):
        resp = self.client.get(reverse('inventory:order-delete',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_post_order_delete_form(self):
        resp = self.client.get(reverse('inventory:order-delete',
            kwargs={
                'pk': models.Order.objects.latest('pk').pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_get_order_detail(self):
        resp = self.client.get(reverse('inventory:order-detail',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_receive_from_order(self):
        resp = self.client.get(reverse('inventory:receive-from-order',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertTrue(resp.status_code == 302)

    def test_get_stock_receipt_form(self):
        resp = self.client.get(reverse('inventory:stock-receipt-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_stock_receipt_form(self):
        inv_b4 = Account.objects.get(pk=1004).balance
        resp = self.client.post(reverse('inventory:stock-receipt-create'),
            data={
                'order': self.order.pk,
                'receive_date': TODAY,
                'note': 'test note',
                'received-items': urllib..parse.quote(json.dumps({
                    'item-' + str(self.order_item.pk) : 2
                }))
            })
        self.assertTrue(resp.status_code == 302)
        #test the created transaction
        self.assertEqual(Account.objects.get(pk=1004).balance, inv_b4 + 16 )

    def test_get_config_view(self):
        resp = self.client.get(reverse('inventory:config'))
        self.assertTrue(resp.status_code == 200)

    def test_post_config_view(self):
        resp = self.client.post(reverse('inventory:config'),
            data={
                'inventory_valuation': 'fifo'
            })
        self.assertTrue(resp.status_code == 302)

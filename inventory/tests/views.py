
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
        

class CommonViewTests(TestCase):
    fixtures = ['accounts.json','employees.json','common.json', 
    'invoicing.json','journals.json', 'inventory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client
        cls.UNIT_DATA = {
            'name': 'Test Unit',
            'description': 'TEst Description',
            'eval_string': '1+1',
            'is_derived': False,
        }
        cls.CATEGORY_DATA = {
            'name': 'Test Category',
            'description': "TEst Description",
            'parent': 1
        }
    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)
        
    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_unit_form(self):
        resp = self.client.get(reverse('inventory:unit-create'))
        self.assertTrue(resp.status_code == 200)

    def test_get_home_page(self):
        resp = self.client.get(reverse('inventory:home'))
        self.assertTrue(resp.status_code == 200)


    def test_get_config_view(self):
        resp = self.client.get(reverse('inventory:config', 
            kwargs={'pk': 1}))
        self.assertTrue(resp.status_code == 200)

    def test_post_config_view(self):
        resp = self.client.post(reverse('inventory:config',
            kwargs={'pk': 1}),
            data={
                'inventory_valuation_method': 1,
                'product_sales_pricing_method': 1,
                'order_template_theme': 1,
                'inventory_check_frequency': 1,
                'inventory_check_date': 1,
                'use_warehousing_model': True,
                'use_storage_media_model': True,
                'stock_valuation_period': 365,
            })
        self.assertTrue(resp.status_code == 302)

    def test_post_unit_form(self):
        resp = self.client.post(reverse('inventory:unit-create'), 
            data=self.UNIT_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_unit_update_form(self):
        resp = self.client.get(reverse('inventory:unit-update',
            kwargs={'pk': 1}))
        self.assertTrue(resp.status_code == 200)

    def test_post_unit_update_form(self):
        resp = self.client.post(reverse('inventory:unit-update',
            kwargs={'pk': 1}), 
            data=self.UNIT_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_unit_list_page(self):
        resp = self.client.get(reverse('inventory:unit-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_unit_detail_page(self):
        resp = self.client.get(reverse('inventory:unit-detail',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_category_create_page(self):
        resp = self.client.get(reverse('inventory:category-create'))
        self.assertEqual(resp.status_code, 200)

    def test_post_category_create_page(self):
        resp = self.client.post(reverse('inventory:category-create'),
            data=self.CATEGORY_DATA)
        
        self.assertEqual(resp.status_code, 302)

    def test_get_category_update_page(self):
        resp = self.client.get(reverse('inventory:category-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_category_update_page(self):
        resp = self.client.post(reverse('inventory:category-update',
            kwargs={'pk': 1}), data=self.CATEGORY_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_category_list_page(self):
        resp = self.client.get(reverse('inventory:category-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_category_detail_page(self):
        resp = self.client.get(reverse('inventory:category-detail',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_inventory_controller_create_page(self):
        resp = self.client.get(reverse('inventory:create-inventory-controller'))
        self.assertEqual(resp.status_code, 200)

    def test_post_inventory_controller_create_page(self):
        resp = self.client.post(reverse(
            'inventory:create-inventory-controller'), 
                data={
                    'employee': 1,
                    'can_authorize_equipment_requisitions': True,
                    'can_authorize_consumables_requisitions': True
                })
        self.assertEqual(resp.status_code, 302)

    def test_inventory_controller_list_page(self):
        resp = self.client.get(reverse('inventory:inventory-controller-list'))
        self.assertEqual(resp.status_code, 200)


class InventoryManagementViewTests(TestCase):
    fixtures = ['accounts.json','employees.json','common.json', 
    'invoicing.json','journals.json', 'inventory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)
        
    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_stock_receipt_form(self):
        resp = self.client.get(reverse('inventory:stock-receipt-create',
            kwargs={'pk': 1}))
        self.assertTrue(resp.status_code == 200)

    def test_post_stock_receipt_form(self):
        inv_b4 = Account.objects.get(pk=1004).balance
        resp = self.client.post(reverse('inventory:stock-receipt-create',
            kwargs={'pk': 1}),
            data={
                'receive_date': TODAY,
                'order': 1,
                'note': 'test note',
                'received_by': 1,
                'warehouse': 1,
                'received-items': urllib.parse.quote(json.dumps([
                    {
                        'orderItem': self.order_item.pk, 
                        'quantity': 1,
                        'medium': ""
                }]))
            })
        self.assertTrue(resp.status_code == 302)

    def test_get_goods_received_page(self):
        resp = self.client.get(reverse('inventory:goods-received',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_inventory_check_create_page(self):
        resp = self.client.get(reverse('inventory:create-inventory-check',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_inventory_check_create_page(self):
        resp = self.client.post(reverse('inventory:create-inventory-check',
            kwargs={'pk': 1}), data={
               'date': TODAY.strftime('%m/%d/%Y'),
               'adjusted_by': 1,
               'warehouse': 1,
               'comments': 'Test comments',
               'adjustments': urllib.parse.quote(json.dumps([
                   {
                       'warehouse_item': 1,
                       'note': 'adj note',
                       'adjustment': 1
                    }
               ]))
            })
        self.assertEqual(resp.status_code, 302)

    def test_get_inventory_check_list_page(self):
        resp = self.client.get(reverse('inventory:inventory-check-list',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_inventory_check_summary_page(self):
        resp = self.client.get(reverse('inventory:inventory-check-summary',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_inventory_scrapping_page(self):
        resp = self.client.get(reverse('inventory:scrap-inventory', 
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_inventory_scrapping_page(self):
        resp = self.client.post(reverse('inventory:scrap-inventory', 
            kwargs={'pk': 1}), data={
                'warehouse': 1,
                'date': TODAY.strftime('%m/%d/%Y'),
                'controller': 1,
                'comments': 'Test',
                'items': urllib.parse.quote(json.dumps([{
                    'pk': 1,
                    'quantity': 1,
                    'note': 'Test'
                }]))


            })
        self.assertEqual(resp.status_code, 302)

    def test_get_inventory_scrapping_history_page(self):
        resp = self.client.get(reverse('inventory:scrap-history', 
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_inventory_scrapping_page(self):
        resp = self.client.get(reverse('inventory:scrapping-report', 
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)


class ItemViewTests(TestCase):
    fixtures = ['accounts.json','employees.json','common.json', 
    'invoicing.json','journals.json', 'inventory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client
        cls.COMMON_DATA = {
            'name' : 'Test Item',
            'unit' : cls.unit.pk,
            'length': 0.0,
            'width': 0.0,
            'height': 0.0,
            'unit_purchase_price' : 8,
            'description' : 'Test Description',
            'supplier' : cls.supplier.pk,
            'quantity' : 10,
            'category' : cls.category.pk
        }
        cls.PRODUCT_DATA = {
            'margin' : 0.2,
            'markup' : 0.2,
            'direct_price' : 10,
            'pricing_method': 2,
            'minimum_order_level' : 0,
            'maximum_stock_level' : 20,
        }
        cls.EQUIPMENT_DATA = {
            'condition': 'good',
            'asset_data': 1
        }
        cls.CONSUMABLE_DATA = {
            'minimum_order_level' : 0,
            'maximum_stock_level' : 20,
        }

        cls.EQUIPMENT_DATA.update(cls.COMMON_DATA)
        cls.PRODUCT_DATA.update(cls.COMMON_DATA)
        cls.CONSUMABLE_DATA.update(cls.COMMON_DATA)

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)
        
    def setUp(self):
        self.client.login(username='Testuser', password='123')

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
    
    #equipment

    def test_get_equipment_form(self):
        resp = self.client.get(reverse('inventory:equipment-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_equipment_form(self):
        resp = self.client.post(reverse('inventory:equipment-create'),
            data=self.EQUIPMENT_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_equipment_list(self):
        resp = self.client.get(reverse('inventory:equipment-list'))
        self.assertTrue(resp.status_code == 200)

    def test_get_equipment_update_form(self):
        resp = self.client.get(reverse('inventory:equipment-update',
            kwargs={
                'pk': self.equipment.pk
            }))
        self.assertTrue(resp.status_code == 200)
    
    def test_post_equipment_update_form(self):
        resp = self.client.post(reverse('inventory:equipment-update',
            kwargs={
                'pk': self.equipment.pk
            }), data=self.EQUIPMENT_DATA)
        self.assertTrue(resp.status_code == 302)
    
    def test_get_equipment_detail(self):
        resp = self.client.get(reverse('inventory:equipment-detail',
            kwargs={
                'pk': self.equipment.pk
            }))
        self.assertTrue(resp.status_code == 200)
    
    #consumable

    def test_get_consumable_form(self):
        resp = self.client.get(reverse('inventory:consumable-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_consumable_form(self):
        resp = self.client.post(reverse('inventory:consumable-create'),
            data=self.CONSUMABLE_DATA)
        self.assertTrue(resp.status_code == 302)

    def test_get_consumable_list(self):
        resp = self.client.get(reverse('inventory:consumable-list'))
        self.assertTrue(resp.status_code == 200)

    def test_get_consumable_update_form(self):
        resp = self.client.get(reverse('inventory:consumable-update',
            kwargs={
                'pk': self.consumable.pk
            }))
        self.assertTrue(resp.status_code == 200)
    
    def test_post_consumable_update_form(self):
        resp = self.client.post(reverse('inventory:consumable-update',
            kwargs={
                'pk': self.consumable.pk
            }), data=self.CONSUMABLE_DATA)
        self.assertTrue(resp.status_code == 302)


class OrderViewTests(TestCase):
    fixtures = ['accounts.json','employees.json','common.json', 
    'invoicing.json','journals.json', 'inventory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client
        cls.ORDER_DATA = {
            'expected_receipt_date' : TODAY,
            'date' : TODAY,
            'deferred_date' : TODAY,
            'supplier' : cls.supplier.pk,
            'bill_to' : 'Test Bill to',
            'ship_to' : cls.warehouse.pk,
            'tax': 1,
            'type_of_order': 0,
            'tracking_number' : '34234',
            'notes' : 'Test Note',
            'status' : 'draft',
            'items': urllib.parse.quote(json.dumps([{
                'pk': 'P' + str(cls.product.pk),
                'quantity': 10,
                'order_price': 10
                }])),
            'issuing_inventory_controller': 1
        }

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)
        
    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_order_form(self):
        resp = self.client.get(reverse('inventory:order-create'))
        self.assertTrue(resp.status_code == 200)

    def test_post_order_form(self):
        resp = self.client.post(reverse('inventory:order-create'), 
        data=self.ORDER_DATA)
        self.assertTrue(resp.status_code == 302)
    
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

    def test_get_order_status(self):
        resp = self.client.get(reverse('inventory:order-status',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertTrue(resp.status_code == 200)

    def test_get_order_email(self):
        resp = self.client.get(reverse('inventory:order-email',
            kwargs={'pk': 1}))
        self.assertTrue(resp.status_code == 200)

    #order pdf assume that the detail view covers it
    #order emaiL only use the get view

class SupplierViewTests(TestCase):
    fixtures = ['accounts.json','employees.json','common.json', 
    'invoicing.json','journals.json', 'inventory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)

        cls.SUPPLIER_DATA = {
            'individual': 1,
        }

    def setUp(self):
        self.client.login(username='Testuser', password='123')

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


class WarehouseViewTests(TestCase):
    fixtures = ['accounts.json','employees.json','common.json', 
    'invoicing.json','journals.json', 'inventory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client
        cls.WAREHOUSE_DATA = {
            'name': 'Test Name',
            'address': 'TEst Address',
            'description': 'Test Description',
            'inventory_controller': 1,
            'length': 0,
            'width': 0,
            'height': 0
        }
        cls.STORAGE_MEDIA_DATA = {
            'warehouse': 1,
            'name': 'Test Name',
            'description': 'TEst Description',
            'unit': 1,
            'length': 0,
            'width': 0,
            'height': 0,
            'capacity': 10

        }

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)


    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_warehouse_create_page(self):
        resp = self.client.get(reverse('inventory:warehouse-create'))
        self.assertEqual(resp.status_code, 200)

    def test_post_warehouse_create_page(self):
        resp = self.client.post(reverse('inventory:warehouse-create'),
            data=self.WAREHOUSE_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_warehouse_update_page(self):
        resp = self.client.get(reverse('inventory:warehouse-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_warehouse_update_page(self):
        resp = self.client.post(reverse('inventory:warehouse-update',
            kwargs={'pk': 1}), data=self.WAREHOUSE_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_warehouse_list_page(self):
        resp = self.client.get(reverse('inventory:warehouse-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_warehouse_detail_page(self):
        resp = self.client.get(reverse('inventory:warehouse-detail',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_warehouse_delete_page(self):
        resp = self.client.get(reverse('inventory:warehouse-delete',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_storage_media_create_page(self):
        resp = self.client.get(reverse('inventory:storage-media-create',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_storage_media_create_page(self):
        resp = self.client.post(reverse('inventory:storage-media-create',
            kwargs={'pk': 1}), data=self.STORAGE_MEDIA_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_storage_media_update_page(self):
        resp = self.client.get(reverse('inventory:storage-media-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_storage_media_update_page(self):
        resp = self.client.post(reverse('inventory:storage-media-update',
            kwargs={'pk': 1}), data=self.STORAGE_MEDIA_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_storage_media_list_page(self):
        resp = self.client.get(reverse('inventory:storage-media-list',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)


class ReportViewTests(TestCase):
    fixtures = ['accounts.json','employees.json','common.json', 
    'invoicing.json','journals.json', 'inventory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_inventory_report_page(self):
        resp = self.client.get(reverse('inventory:inventory-report'))
        self.assertEqual(resp.status_code, 200)

    def test_outstanding_orders_report(self):
        resp = self.client.get(reverse('inventory:outstanding-orders-report'))
        self.assertEqual(resp.status_code, 200)


class TransferViewTests(TestCase):
    fixtures = ['accounts.json','employees.json','common.json', 
    'invoicing.json','journals.json', 'inventory.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client
        cls.TRANSFER_DATA = {
            'source_warehouse': 1,
            'date': TODAY.strftime('%m/%d/%Y'),
            'expected_completion_date': TODAY.strftime('%m/%d/%Y'), 
            'issuing_inventory_controller': 1,
            'receiving_warehouse': 1,
            'order_issuing_notes': 'Some note',
            'items': urllib.parse.quote(json.dumps([
                {
                    'item': '1 - name',
                    'quantity': 1    
                }
            ]))
        }

        cls.RECEIVE_DATA = {
            'actual_completion_date': TODAY.strftime('%m/%d/%Y'), 
            'receive_notes': 'Some note',
            'receiving_inventory_controller': 1
        }

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_create_transfer_order_page(self):
        resp = self.client.get(reverse('inventory:create-transfer-order',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_create_transfer_order_page(self):
        resp = self.client.post(reverse('inventory:create-transfer-order',
            kwargs={'pk': 1}), data=self.TRANSFER_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_transfer_order_list_page(self):
        resp = self.client.get(reverse('inventory:transfer-order-list',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_transfer_order_detail_page(self):
        resp = self.client.get(reverse('inventory:transfer-order-detail',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_get_receive_transfer_order_page(self):
        resp = self.client.get(reverse('inventory:receive-transfer',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code, 200)

    def test_post_receive_transfer_order_page(self):
        resp = self.client.get(reverse('inventory:receive-transfer', 
            kwargs={'pk': 1}), data=self.RECEIVE_DATA)
        self.assertEqual(resp.status_code, 200)
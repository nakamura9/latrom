
import datetime
import json
import urllib

from django.test import Client, TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone

from accounting.models import Account, JournalEntry, Tax, AccountingSettings
from common_data.models import Organization
from common_data.tests import create_account_models, create_test_user, create_test_common_entities
from inventory import models
from django.contrib.auth.models import User

from .models import create_test_inventory_models
from .model_util import InventoryModelCreator
from employees.tests.model_util import EmployeeModelCreator
from inventory import models
from employees.models import Employee
import copy
from messaging.models import UserProfile

TODAY = datetime.date.today()
from inventory.views import (InventoryReportPDFView,
                             TransactionByVendorPDFView,
                             OutstandingOrderReportPDFView,
                             PaymentsDuePDFView,
                             VendorAverageDaysToDeliverPDFView,
                             VendorBalancePDFView,
                             )
        

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
        create_test_common_entities(cls)
        EmployeeModelCreator(cls).create_employee()
        
        
    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_unit_form(self):
        resp = self.client.get(reverse('inventory:unit-create'))
        self.assertEqual(resp.status_code,  200)

    def test_get_home_page(self):
        resp = self.client.get(reverse('inventory:home'))
        self.assertEqual(resp.status_code,  302)
        #after configuration
        settings = models.InventorySettings.objects.first()
        settings.is_configured = True
        settings.save()
        resp = self.client.get(reverse('inventory:home'))
        self.assertEqual(resp.status_code,  200)
        settings.is_configured = False
        settings.save()

    def test_get_config_view(self):
        resp = self.client.get(reverse('inventory:config', 
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code,  200)

    def test_post_config_view(self):
        resp = self.client.post(reverse('inventory:config',
            kwargs={'pk': 1}),
            data={
                'inventory_valuation_method': 1,
                'default_product_sales_pricing_method': 1,
                'inventory_check_frequency': 1,
                'inventory_check_date': 1,
                'use_warehousing_model': True,
                'use_storage_media_model': True,
            })
        self.assertEqual(resp.status_code,  302)

    def test_post_unit_form(self):
        resp = self.client.post(reverse('inventory:unit-create'), 
            data=self.UNIT_DATA)
        self.assertEqual(resp.status_code, 302)

    def test_get_unit_update_form(self):
        resp = self.client.get(reverse('inventory:unit-update',
            kwargs={'pk': 1}))
        self.assertEqual(resp.status_code,  200)

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
                    'employee': self.employee.pk,
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
        create_test_common_entities(cls)
        InventoryModelCreator(cls).create_inventory_controller()

        
    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_stock_receipt_form(self):
        resp = self.client.get(reverse('inventory:stock-receipt-create',
            kwargs={
                'warehouse': 1,
                'pk': 1
                }))
        self.assertEqual(resp.status_code,  200)

    def test_post_stock_receipt_form(self):
        resp = self.client.post(reverse('inventory:stock-receipt-create',
            kwargs={
                'warehouse': 1,
                'pk': 1
                }),
            data={
                'receive_date': TODAY,
                'order': 1,
                'note': 'test note',
                'received_by': 1,
                'warehouse': 1,
                'received-items': urllib.parse.quote(json.dumps([
                    {
                        'item': '1 - some item', 
                        'quantity_to_move': 1,
                        'receiving_location': "1 - some location"
                }]))
            })
        
        self.assertEqual(resp.status_code,  302)

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
               'check-table': urllib.parse.quote(json.dumps([
                   {
                       'item': '1 - item',
                       'quantity': 2,
                       'measured': 1
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

    

    def test_post_inventory_scrapping_page(self):
        resp = self.client.post(reverse('inventory:scrap-inventory', 
            kwargs={'pk': 1}), data={
                'warehouse': 1,
                'date': TODAY.strftime('%m/%d/%Y'),
                'controller': 1,
                'comments': 'Test',
                'items': urllib.parse.quote(json.dumps([{
                    'item': "1 - item",
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
            'category' : cls.category.pk,
            'initial_quantity': 0
        }
        cls.PRODUCT_DATA = {
            'margin' : 0.2,
            'markup' : 0.2,
            'direct_price' : 10,
            'pricing_method': 2,
            'minimum_order_level' : 0,
            'maximum_stock_level' : 20,
            'type': 0,
            'tax': Tax.objects.create(name='tax', rate=15).pk
        }
        cls.EQUIPMENT_DATA = {
            'type': 1
        }
        cls.CONSUMABLE_DATA = {
            'minimum_order_level' : 0,
            'maximum_stock_level' : 20,
            'type': 2
        }

        cls.EQUIPMENT_DATA.update(cls.COMMON_DATA)
        cls.PRODUCT_DATA.update(cls.COMMON_DATA)
        cls.CONSUMABLE_DATA.update(cls.COMMON_DATA)

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)
        create_test_common_entities(cls)

        
    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_product_form(self):
        resp = self.client.get(reverse('inventory:product-create'))
        self.assertEqual(resp.status_code,  200)

    def test_post_product_form(self):
        resp = self.client.post(reverse('inventory:product-create'),
            data=self.PRODUCT_DATA)
        
        self.assertEqual(resp.status_code,  302)

    def test_get_product_list(self):
        resp = self.client.get(reverse('inventory:product-list'))
        self.assertEqual(resp.status_code,  200)

    def test_get_product_update_form(self):
        resp = self.client.get(reverse('inventory:product-update',
            kwargs={
                'pk': self.product.pk
            }))
        self.assertEqual(resp.status_code,  200)
    
    def test_post_product_update_form(self):
        resp = self.client.post(reverse('inventory:product-update',
            kwargs={
                'pk': self.product.pk
            }), data=self.PRODUCT_DATA)
        self.assertEqual(resp.status_code,  302)

    def test_get_product_delete_form(self):
        resp = self.client.get(reverse('inventory:product-delete',
            kwargs={
                'pk': self.product.pk
            }))
        self.assertEqual(resp.status_code,  200)

    def test_post_product_delete_form(self):
        resp = self.client.post(reverse('inventory:product-delete',
            kwargs={
                'pk': models.InventoryItem.objects.latest('pk').pk
            }))
        self.assertEqual(resp.status_code,  302)
    
    def test_get_product_detail(self):
        resp = self.client.get(reverse('inventory:product-detail',
            kwargs={
                'pk': self.product.pk
            }))
        self.assertEqual(resp.status_code,  200)
    
    #equipment

    def test_get_equipment_form(self):
        resp = self.client.get(reverse('inventory:equipment-create'))
        self.assertEqual(resp.status_code,  200)

    def test_post_equipment_form(self):
        resp = self.client.post(reverse('inventory:equipment-create'),
            data=self.EQUIPMENT_DATA)        
        
        self.assertEqual(resp.status_code,  302)

    def test_post_equipment_with_asset_form(self):
        self.EQUIPMENT_DATA.update({
                'record_as_asset': True,
                'asset_category': 0,
                'unit_purchase_price': 100,
                'initial_value': 100,
                'salvage_value': 0,
                'date_purchased': datetime.date.today(),
                'depreciation_period': 5
            })
        resp = self.client.post(reverse('inventory:equipment-create'),
            data=self.EQUIPMENT_DATA)        
        
        self.assertEqual(resp.status_code,  302)

        self.EQUIPMENT_DATA.update({
            'unit_purchase_price': 8
        })

    def test_get_equipment_list(self):
        resp = self.client.get(reverse('inventory:equipment-list'))
        self.assertEqual(resp.status_code,  200)

    def test_get_equipment_update_form(self):
        resp = self.client.get(reverse('inventory:equipment-update',
            kwargs={
                'pk': self.equipment.pk
            }))
        self.assertEqual(resp.status_code,  200)
    
    def test_post_equipment_update_form(self):
        resp = self.client.post(reverse('inventory:equipment-update',
            kwargs={
                'pk': self.equipment.pk
            }), data=self.EQUIPMENT_DATA)
        self.assertEqual(resp.status_code,  302)

    def test_post_equipment_with_asset_update_form(self):
        self.EQUIPMENT_DATA.update({
                'record_as_asset': True,
                'asset_category': 0,
                'initial_value': 100,
                'unit_purchase_price': 100,
                'salvage_value': 0,
                'date_purchased': datetime.date.today(),
                'depreciation_period': 5
            })

        resp = self.client.post(reverse('inventory:equipment-update',
            kwargs={
                'pk': self.equipment.pk
            }), data=self.EQUIPMENT_DATA)
        
        self.assertEqual(resp.status_code,  302)
        
        self.EQUIPMENT_DATA.update({
            'unit_purchase_price': 8
        })
    
    def test_get_equipment_detail(self):
        resp = self.client.get(reverse('inventory:equipment-detail',
            kwargs={
                'pk': self.equipment.pk
            }))
        self.assertEqual(resp.status_code,  200)
    
    #consumable

    def test_get_consumable_form(self):
        resp = self.client.get(reverse('inventory:consumable-create'))

        self.assertEqual(resp.status_code,  200)

    def test_post_consumable_form(self):
        resp = self.client.post(reverse('inventory:consumable-create'),
            data=self.CONSUMABLE_DATA)
        self.assertEqual(resp.status_code,  302)

    def test_get_consumable_list(self):
        resp = self.client.get(reverse('inventory:consumable-list'))
        self.assertEqual(resp.status_code,  200)

    def test_get_consumable_update_form(self):
        resp = self.client.get(reverse('inventory:consumable-update',
            kwargs={
                'pk': self.consumable.pk
            }))
        self.assertEqual(resp.status_code,  200)
    
    def test_post_consumable_update_form(self):
        resp = self.client.post(reverse('inventory:consumable-update',
            kwargs={
                'pk': self.consumable.pk
            }), data=self.CONSUMABLE_DATA)
        self.assertEqual(resp.status_code,  302)


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
            'due' : TODAY,
            'deferred_date' : TODAY,
            'supplier' : cls.supplier.pk,
            'bill_to' : 'Test Bill to',
            'ship_to' : cls.warehouse.pk,
            'tax': 1,
            'tracking_number' : '34234',
            'notes' : 'Test Note',
            'status' : 'draft',
            'items': urllib.parse.quote(json.dumps([{
                'item': str(cls.product.pk) + ' - Name',
                'quantity': 10,
                'unit': "1 - unit",
                'order_price': 10
                }])),
            'issuing_inventory_controller': 1
        }

    @classmethod
    def setUpTestData(cls):
        create_account_models(cls)
        create_test_user(cls)
        create_test_inventory_models(cls)
        create_test_common_entities(cls)
        InventoryModelCreator(cls).create_inventory_controller()
        UserProfile.objects.create(
            user=User.objects.get(username='Testuser'),
            email_address="test@address.com",
            email_password='123',
        )
        
    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_order_form(self):
        resp = self.client.get(reverse('inventory:order-create'))
        self.assertEqual(resp.status_code,  200)

    def test_get_order_form_with_supplier(self):
        resp = self.client.get(reverse('inventory:order-create', kwargs={
            'supplier': self.supplier.pk
        }))
        self.assertEqual(resp.status_code,  200)

    def test_post_order_form(self):
        resp = self.client.post(reverse('inventory:order-create'), 
        data=self.ORDER_DATA)
        self.assertEqual(resp.status_code,  302)

    def test_post_order_form_with_error(self):
        data = copy.deepcopy(self.ORDER_DATA)
        data['items'] = ""
        resp = self.client.post(reverse('inventory:order-create'), 
        data=data)

        self.assertEqual(resp.status_code,  302)

    def test_post_order_form_with_payment(self):
        data = copy.deepcopy(self.ORDER_DATA)
        data['payment'] = True
        resp = self.client.post(reverse('inventory:order-create'), 
            data=data)

        self.assertEqual(resp.status_code,  302)

    
    def test_get_order_list(self):
        resp = self.client.get(reverse('inventory:order-list'))
        self.assertEqual(resp.status_code,  200)

    def test_get_order_update_form(self):
        resp = self.client.get(reverse('inventory:order-update',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertEqual(resp.status_code,  200)

    def test_post_order_update_form(self):
        resp = self.client.post(reverse('inventory:order-update',
            kwargs={
                'pk': self.order.pk
            }), data=self.ORDER_DATA)
        self.assertEqual(resp.status_code,  302)

    def test_get_order_delete_form(self):
        resp = self.client.get(reverse('inventory:order-delete',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertEqual(resp.status_code,  200)

    def test_post_order_delete_form(self):
        resp = self.client.get(reverse('inventory:order-delete',
            kwargs={
                'pk': models.Order.objects.latest('pk').pk
            }))
        self.assertEqual(resp.status_code,  200)

    def test_get_order_detail(self):
        resp = self.client.get(reverse('inventory:order-detail',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertEqual(resp.status_code,  200)

    def test_get_order_status(self):
        resp = self.client.get(reverse('inventory:order-status',
            kwargs={
                'pk': self.order.pk
            }))
        self.assertEqual(resp.status_code,  200)

    def test_get_order_email(self):
        with self.assertRaises(Exception):
            self.client.get(reverse('inventory:order-email',
            kwargs={'pk': 1}))
        
        #self.assertEqual(resp.status_code,  200)

    def test_get_shipping_costs_detail_view(self):
        resp = self.client.get("/inventory/order/expense/list/1")
        self.assertEqual(resp.status_code, 200)
        
    def test_get_shipping_form_view(self):
        resp = self.client.get("/inventory/order-expense/1")
        self.assertEqual(resp.status_code, 200)

    def test_post_shipping_form(self):
        resp = self.client.post("/inventory/order-expense/1", data={
            'date': datetime.date.today(),
            'description': 'Some description',
            'recorded_by': 1,
            'amount': 10,
            'reference': "123"
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_debit_note_create_view(self):
        resp = self.client.get('/inventory/debit-note/create/1')
        self.assertEqual(resp.status_code, 200)

    def test_post_debit_note_create_view(self):
        resp = self.client.post('/inventory/debit-note/create/1', 
            data={
                'returned-items': urllib.parse.quote(json.dumps([{
                    'item': '1 -item',
                    'quantity': 1,
                    'returned_quantity': 1
                }])),
                'date': datetime.date.today(),
                'order': 1,
                'comments': 'some comment'
            })
        
        self.assertEqual(resp.status_code, 302)

    def test_get_debit_note_list_view(self):
        resp = self.client.get('/inventory/debit-note/list/1')
        self.assertEqual(resp.status_code, 200)


    def test_debit_note_detail_view(self):
        resp = self.client.get('/inventory/debit-note/detail/1')
        self.assertEqual(resp.status_code, 200)

    def test_get_order_payment_view(self):
        resp = self.client.get(reverse('inventory:order-payment', kwargs={
            'pk': self.order.pk
        }))
        self.assertEqual(resp.status_code, 200)

    def test_post_order_payment_view(self):
        resp = self.client.post(reverse('inventory:order-payment', kwargs={
            'pk': self.order.pk
        }), data={
            'order': self.order.pk,
            'amount': 100,
            'date': datetime.date.today(),
            'comments': 'comments'
        })
        self.assertEqual(resp.status_code, 302)

    def test_get_order_payment_list_view(self):
        resp = self.client.get(reverse('inventory:order-payment-list', kwargs={
            'pk': self.order.pk
        }))
        self.assertEqual(resp.status_code, 200)

    '''def test_verify_order_view(self):
        resp = self.client.get(reverse('inventory:verify-order', kwargs={
            'pk': self.order.pk
        }), data={
            'user': 1,
            'password': '123'
            })
        self.assertEqual(resp.status_code, 302)

    #order pdf assume that the detail view covers it
    #order emaiL only use the get view'''


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
        create_test_common_entities(cls)

        cls.sup_ind = models.Supplier.objects.create(
            individual=cls.individual,
        )


        cls.SUPPLIER_DATA = {
            'vendor_type': 'individual',
            'name': 'test supplier'
        }

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_get_supplier_create(self):
        resp = self.client.get('/inventory/supplier/create')
        self.assertEqual(resp.status_code,  200)

    def test_post_supplier_create(self):
        resp = self.client.post('/inventory/supplier/create',
            data=self.SUPPLIER_DATA)
        self.assertEqual(resp.status_code,  302)

    def test_post_supplier_create_organization(self):
        resp = self.client.post('/inventory/supplier/create',
            data={
                'vendor_type': 'organization',
                'name': 'vendor',
                'address': 'somewhere'
            })
        self.assertEqual(resp.status_code,  302)

    def test_get_supplier_list(self):
        resp = self.client.get('/inventory/supplier/list/')
        self.assertEqual(resp.status_code,  200)

    def test_get_supplier_update(self):
        resp = self.client.get(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.supplier.pk
            }))
        self.assertEqual(resp.status_code,  200)

    def test_get_supplier_update_individual(self):
        
        resp = self.client.get(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.sup_ind.pk
            }))
        self.assertEqual(resp.status_code,  200)

    def test_post_supplier_update_no_swap_org(self):
        resp = self.client.post(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.supplier.pk
            }), data={
                "vendor_type": "organization",
                "name": "other supplier"
                })
        self.assertEqual(resp.status_code,  302)

    def test_post_supplier_update_no_swap_individual(self):
        resp = self.client.post(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.sup_ind.pk
            }), data=self.SUPPLIER_DATA)
        self.assertEqual(resp.status_code,  302)


    def test_post_supplier_update_swap_org(self):
        resp = self.client.post(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.supplier.pk
            }), data=self.SUPPLIER_DATA)
        self.assertEqual(resp.status_code,  302)

    def test_post_supplier_update_swap_individual(self):
        resp = self.client.post(reverse('inventory:supplier-update',
            kwargs={
                'pk': self.sup_ind.pk
            }), data={
                'vendor_type': 'organization',
                'name': 'swapped'
            })
        self.assertEqual(resp.status_code,  302)

    def test_get_supplier_delete(self):
        resp = self.client.get(reverse('inventory:supplier-delete',
            kwargs={
                'pk': self.supplier.pk
            }))
        self.assertEqual(resp.status_code,  200) 


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
        create_test_common_entities(cls)
        InventoryModelCreator(cls).create_inventory_controller()




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
        create_test_common_entities(cls)


    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_inventory_report_page(self):
        resp = self.client.get(reverse('inventory:inventory-report'))
        self.assertEqual(resp.status_code, 200)

    def test_inventory_report_pdf_view(self):
        req = RequestFactory().get(reverse('inventory:inventory-report'))
        resp = InventoryReportPDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_outstanding_orders_report(self):
        resp = self.client.get(reverse('inventory:outstanding-orders-report'))
        self.assertEqual(resp.status_code, 200)

    def test_outstanding_orders_pdf_view(self):
        req = RequestFactory().get(reverse(
            'inventory:outstanding-orders-report'))
        resp = OutstandingOrderReportPDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_payments_due_report_page(self):
        resp = self.client.get(reverse('inventory:payments-due-report'))
        self.assertEqual(resp.status_code, 200)

    def test_payments_due_pdf(self):
        req = RequestFactory().get(reverse('inventory:payments-due-pdf'))
        resp = PaymentsDuePDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_vendor_average_days_to_deliver(self):
        resp = self.client.get(reverse(
            'inventory:vendor-average-days-to-deliver-report'))
        self.assertEqual(resp.status_code, 200)

    def test_vendor_average_days_to_deliver_pdf(self):
        req = RequestFactory().get(reverse(
            'inventory:vendor-average-days-to-deliver-pdf'))
        resp = VendorAverageDaysToDeliverPDFView.as_view()(req)
        self.assertEqual(resp.status_code, 200)

    def test_vendor_balance_report(self):
        resp =self.client.get(reverse('inventory:vendor-balance-report'))
        self.assertEqual(resp.status_code, 200)

    def test_vendor_balance_report(self):
        req =RequestFactory().get(reverse('inventory:vendor-balance-report'))
        resp =VendorBalancePDFView.as_view()(req)

        self.assertEqual(resp.status_code, 200)

    def test_transaction_by_vendor_form(self):
        resp = self.client.get(reverse('inventory:vendor-transactions-form'))
        self.assertEqual(resp.status_code, 200)

    def test_vendor_transactions_report(self):
        resp = self.client.get(reverse('inventory:vendor-transactions-report'), 
            data={
                'start_period': datetime.date.today() - datetime.timedelta(days=365),
                'end_period': datetime.date.today()
            })
        self.assertEqual(resp.status_code, 200)

    def test_vendor_transactions_pdf_report(self):
        kwargs = {
                'start': (datetime.date.today() \
                    - datetime.timedelta(days=365)).strftime('%d %B %Y'),
                'end': datetime.date.today().strftime('%d %B %Y')
            }
        req = RequestFactory().get(reverse(
            'inventory:vendor-transactions-pdf', kwargs=kwargs))
        resp = TransactionByVendorPDFView.as_view()(req, **kwargs)
        
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
        create_test_common_entities(cls)
        InventoryModelCreator(cls).create_inventory_controller()



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
            kwargs={
                'warehouse': 1,
                'pk': 1
                }))
        self.assertEqual(resp.status_code, 200)

    def test_post_receive_transfer_order_page(self):
        resp = self.client.get(reverse('inventory:receive-transfer', 
            kwargs={
                'warehouse': 1,
                'pk': 1
                }), data=self.RECEIVE_DATA)
        self.assertEqual(resp.status_code, 200)


class ConfigWizardTests(TestCase):
    fixtures = ['common.json', 'journals.json', 'settings.json', 'accounts.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.client = Client()
        

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_superuser(username="Testuser", email="admin@test.com", password="123")

    def setUp(self):
        self.client.login(username='Testuser', password='123')

    def test_inventory_wizard(self):
        config_data = {
            'config_wizard-current_step': 0,
            '0-inventory_check_date': 5,
            '0-inventory_check_frequency': 1,
            '0-default_product_sales_pricing_method': 1,
            '0-inventory_valuation_method': 1
        }

        employee_data = {
            '1-first_name': 'first',
            '1-last_name': 'last',
            '1-leave_days': 1,
            '1-pin': 1000,
            'config_wizard-current_step': 1,
        }

        controller_data = {
            'config_wizard-current_step': 2,
            '2-employee': 1
        }

        warehouse_data = {
            'config_wizard-current_step': 3,
            '3-name': 'name',
            '3-address': 'address',
            '3-length': 0,
            '3-width': 0,
            '3-height': 0,
        }

        supplier_data = {
            'config_wizard-current_step': 4,
            '4-vendor_type': 'individual',
            '4-name': 'caleb kandoro'
        }

        data_list = [config_data, employee_data, controller_data, 
            warehouse_data, supplier_data]

        for step, data in enumerate(data_list, 1):

            try:
                resp = self.client.post(reverse('inventory:config-wizard'), 
                    data=data)

                if step == len(data_list):

                    self.assertEqual(resp.status_code, 302)
                else:
                    self.assertEqual(resp.status_code, 200)
                    if resp.context.get('form'):
                        if hasattr(resp.context['form'], 'errors'):
                            print(resp.context['form'].errors)
            except ValueError:
                pass
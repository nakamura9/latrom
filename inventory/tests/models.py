import datetime
from decimal import Decimal as D
import json
import urllib

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounting.models import Account, JournalEntry, Tax
from common_data.models import Organization

from common_data.tests import create_account_models, create_test_user
from inventory import models
from invoicing.models import SalesInvoiceLine, SalesInvoice, Customer
from employees.models import Employee


TODAY = datetime.date.today()

def create_test_inventory_models(cls):
    create_account_models(cls)
    if not hasattr(cls, 'organization'):
        cls.organization = Organization.objects.create(
            legal_name = 'test business'
        )

    cls.supplier = models.Supplier.objects.create(
            organization=cls.organization,
            account = cls.account_c
            )

    cls.unit = models.UnitOfMeasure.objects.create(
            name='Test Unit',
            description='Test description'
        )
    cls.category = models.Category.objects.create(
            name='Test Category',
            description='Test description'
        )

    cls.product = models.Product.objects.create(
            name='test name',
            unit=cls.unit,
            pricing_method=0, #KISS direct pricing
            direct_price=10,
            margin=0.5,
            unit_purchase_price=10,
            description='Test Description',
            supplier = cls.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = cls.category
        )

    cls.equipment = models.Equipment.objects.create(
        name='test equipment',
            unit=cls.unit,
            unit_purchase_price=10,
            description='Test Description',
            supplier = cls.supplier,
            category = cls.category,
            condition = "excellent",
            asset_data = cls.asset
            
    )
    cls.consumable = models.Consumable.objects.create(
        name='test comsumable',
            unit=cls.unit,
            unit_purchase_price=10,
            description='Test Description',
            supplier = cls.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = cls.category
    )
    cls.raw_material = models.RawMaterial.objects.create(
        name='test raw material',
            unit=cls.unit,
            unit_purchase_price=10,
            description='Test Description',
            supplier = cls.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = cls.category
    )
    
    cls.warehouse = models.WareHouse.objects.create(
        name='Test Location',
        address='Test Address'
    )
    cls.medium = models.StorageMedia.objects.create(
            name="Test Medium",
            warehouse=cls.warehouse,
            description="shelves",
        )
    cls.warehouse_item = models.WareHouseItem.objects.create(
        product = cls.product,
        item_type=1,
        quantity =10,
        warehouse = cls.warehouse,
        location=cls.medium
    )
    cls.order = models.Order.objects.create(
            expected_receipt_date = TODAY,
            date = TODAY,
            tax = Tax.objects.first(), #10%
            supplier=cls.supplier,
            bill_to = 'Test Bill to',
            ship_to = cls.warehouse,
            tracking_number = '34234',
            notes = 'Test Note',
            status = 'draft'
        )
    cls.order_item = models.OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            quantity=1,
            order_price=10,
        )
    cls.stock_receipt = models.StockReceipt.objects.create(
            order = cls.order,
            receive_date = TODAY,
            note = 'Test Note',
            fully_received=True,
        )

    cls.check = models.InventoryCheck.objects.create(
        date=TODAY,
        next_adjustment_date=TODAY,
        adjusted_by=Employee.objects.first(),
        warehouse=cls.warehouse,
        comments="Nothing new"
    )

    cls.adjustment = models.StockAdjustment.objects.create(
        warehouse_item=cls.warehouse_item,
        adjustment=1.0,
        note="Too many",
        inventory_check=cls.check
    )

    cls.transfer = models.TransferOrder.objects.create(
        date = TODAY,
        expected_completion_date = TODAY,
        issuing_inventory_controller = Employee.objects.first(),
        receiving_inventory_controller = Employee.objects.first(),
        actual_completion_date = TODAY,
        source_warehouse = cls.warehouse,
        receiving_warehouse = cls.warehouse,
    )
    cls.transfer_line = models.TransferOrderLine.objects.create(
        product=cls.product,
        quantity=1,
        transfer_order=cls.transfer
    )
    cls.scrap = models.InventoryScrappingRecord.objects.create(
        date=TODAY,
        controller=Employee.objects.first(),
        warehouse=cls.warehouse
    )
    cls.scrap_line = models.InventoryScrappingRecordLine.objects.create(
        product=cls.product,
        quantity=1,
        scrapping_record=cls.scrap
    )


class CommonModelTests(TestCase):
    fixtures = ['common.json', 'employees.json','inventory.json','accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_test_inventory_models(cls)

    def test_update_inventory_settings(self):
        obj = models.InventorySettings.objects.first()
        obj.inventory_check_date=22
        obj.save()
    
    def test_create_invetory_controller(self):
        obj = models.InventoryController.objects.create(
            employee = Employee.objects.first(),
            can_authorize_equipment_requisitions = True,
            can_authorize_consumables_requisitions = True
        )
        self.assertIsInstance(obj, models.InventoryController)
    
    def test_create_supplier(self):
        org = Organization.objects.create(
            legal_name="Test org",
        )
        org = models.Supplier.objects.create(
            organization=org
        )
        self.assertIsInstance(org, models.Supplier)
        

    def test_supplier_name(self):
        self.assertIsInstance(self.supplier.name, str)

    def test_supplier_is_organization(self):
        self.assertTrue(self.supplier.is_organization)

    def test_supplier_email(self):
        self.assertIsInstance(self.supplier.email, str)
    
    def test_supplier_address(self):
        self.assertIsInstance(self.supplier.address, str)

    def test_create_unit_of_measure(self):
        obj = models.UnitOfMeasure.objects.create(
            name='Test unit',
            description="description",
            is_derived=True
        )
        self.assertIsInstance(obj, models.UnitOfMeasure)
        obj.delete()

    def test_unit_derived_units(self):
        base = models.UnitOfMeasure.objects.create(
            name='Test unit',
            description="description",
            is_derived=True
        )
        derived = models.UnitOfMeasure.objects.create(
            name='Test unit',
            description="description",
            is_derived=True,
            base_unit = base
        )

        self.assertEqual(base.derived_units.count(), 1)
        derived.delete()
        base.delete()

    def test_create_category(self):
        obj = models.Category.objects.create(
            name="Test Category",
            parent= None,
            description="Test Description"
        )
        self.assertIsInstance(obj, models.Category)
        obj.delete()

    def test_category_items(self):
        self.assertEqual(self.category.items.count(), 1)

    def test_category_relationships(self):
        parent_one = models.Category.objects.create(
            name="parent one ",
            parent= None,
            description="Test Description"
        )
        parent_two = models.Category.objects.create(
            name="parent two",
            parent= None,
            description="Test Description"
        )
        parent_one_child = models.Category.objects.create(
            name="parent one child",
            parent= parent_one,
            description="Test Description"
        )
        parent_two_child = models.Category.objects.create(
            name="parent two child",
            parent= parent_two,
            description="Test Description"
        )
        parent_two_child_two = models.Category.objects.create(
            name="parent two child two",
            parent= parent_two,
            description="Test Description"
        )
        
        self.assertEqual(parent_one.children.count(), 1)
        self.assertEqual(parent_two.children.count(), 2)
        self.assertEqual(parent_one_child.children.count(), 0)
        self.assertEqual(parent_one.siblings.count(), 
            models.Category.objects.filter(parent__isnull=True).count() - 1)
        self.assertEqual(parent_one_child.siblings.count(), 0)
        self.assertEqual(parent_two_child.siblings.count(), 1)

class ItemManagementModelTests(TestCase):
    fixtures = ['common.json', 'employees.json','inventory.json','accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        create_test_inventory_models(cls)

    def test_create_order(self):
        obj = models.Order.objects.create(
            expected_receipt_date = TODAY,
            date = TODAY,
            type_of_order=1,
            supplier=self.supplier,
            bill_to = 'Test Bill to',
            ship_to = self.warehouse,
            tracking_number = '34234',
            notes = 'Test Note',
            status = 'submitted'    
        )

        self.assertIsInstance(obj, models.Order)
        obj.delete()

    def tearDown(self):
        self.order_item.received = 0
        self.order_item.save()
    

    def test_order_items_set(self):
        self.assertEqual(self.order.items.count(), 1)

    def test_order_total(self):
        self.assertEqual(self.order.total, D('11.0'))

    def test_order_subtotal(self):
        self.assertEqual(self.order.subtotal, 10)

    def test_order_tax_amount(self):
        self.assertEqual(self.order.tax_amount, 1)

    def test_received_total(self):
        self.assertEqual(self.order.received_total, 0)
        self.order_item.received=1
        self.order_item.save()
        self.assertEqual(self.order.received_total, 10)
        
    def test_fully_received(self):
        self.assertFalse(self.order.fully_received)
        self.order_item.received=1
        self.order_item.save()
        self.assertTrue(self.order.fully_received)
        
    def test_percent_received(self):
        self.assertEqual(self.order.percent_received, 0.0)
        self.order_item.received=1
        self.order_item.save()
        self.assertEqual(self.order.percent_received, 100.0)
        
    def test_receive_order(self):
        self.order.receive()
        self.assertTrue(self.order.fully_received)
        
    def test_create_order_item(self):
        obj = models.OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=10,
            order_price=10
        )
        self.assertIsInstance(obj, models.OrderItem)
        obj.delete()

    def test_order_item_get_item(self):
        self.assertIsInstance(self.order_item.item, models.Product)

    def test_order_item_fully_received(self):
        self.assertFalse(self.order_item.fully_received)
        self.order_item.received = 1
        self.order_item.save()
        self.assertTrue(self.order_item.fully_received)
        
    def test_order_item_receive(self):
        self.order_item.receive(1)
        self.assertTrue(self.order_item.fully_received)

    def test_order_item_received_total(self):
        self.order_item.received = 1
        self.order_item.save()
        self.assertEqual(self.order_item.received_total, 10)

    def test_order_item_subtotal(self):
        self.assertEqual(self.order_item.subtotal, 10)

    def test_create_stock_receipt(self):
        obj = models.StockReceipt.objects.create(
            order=self.order,
            received_by=Employee.objects.first(),
            receive_date = TODAY,
            note = "Some note",
        )
        self.assertIsInstance(obj, models.StockReceipt)
        obj.delete()

    def test_stock_receipt_entry(self):
        count = JournalEntry.objects.all().count()
        self.stock_receipt.create_entry()
        self.assertEqual(JournalEntry.objects.all().count(), count + 1)
    
    def test_create_inventory_check(self):
        obj = models.InventoryCheck.objects.create(
            date=TODAY,
            next_adjustment_date=TODAY,
            adjusted_by=Employee.objects.first(),
            warehouse=self.warehouse,
            comments="Nothing new"
        )
        self.assertIsInstance(obj, models.InventoryCheck)
        obj.delete()

    def test_inventory_check_adjustments(self):
        self.assertEqual(self.check.adjustments.count(), 1)

    def test_inventory_adjustment_values(self):
        self.assertEqual(self.check.value_of_all_adjustments, 10)

    def test_create_stock_adjustment(self):
        obj = models.StockAdjustment.objects.create(
            warehouse_item=self.warehouse_item,
            adjustment=1.0,
            note="Too many",
            inventory_check=self.check
        )
        self.assertIsInstance(obj, models.StockAdjustment)
        obj.delete()
        self.warehouse_item.increment(1)
        

    def adjustment_adjustment_value(self):
        self.assertEqual(self.adjustment.adjustment_value, 10)

    def test_prev_quantity(self):
        self.assertEqual(self.adjustment.prev_quantity, 10)

    def test_adjust_inventory(self):
        prev_quantity = self.warehouse_item.quantity
        self.adjustment.adjust_inventory()
        self.assertEqual(self.warehouse_item.quantity, prev_quantity - 1)
        self.warehouse_item.quantity = prev_quantity
        self.warehouse_item.save()

    
    def test_create_transfer_order(self):
        obj = models.TransferOrder.objects.create(
            date = TODAY,
            expected_completion_date = TODAY,
            issuing_inventory_controller = Employee.objects.first(),
            receiving_inventory_controller = Employee.objects.first(),
            actual_completion_date = TODAY,
            source_warehouse = self.warehouse,
            receiving_warehouse = self.warehouse,
        )
        self.assertIsInstance(obj, models.TransferOrder)
        obj.delete()

    def test_complete_transfer_order(self):
        self.transfer.complete()
        self.assertTrue(self.transfer.completed)

    def test_create_transfer_record_line(self):
        obj = models.TransferOrderLine.objects.create(
            product=self.product,
            quantity=1,
            transfer_order=self.transfer
        )
        self.assertIsInstance(obj, models.TransferOrderLine)
        obj.delete()

    def test_create_inventory_scrapping_record(self):
        obj = models.InventoryScrappingRecord.objects.create(
            date=TODAY,
            controller=Employee.objects.first(),
            warehouse=self.warehouse
        )
        self.assertIsInstance(obj, models.InventoryScrappingRecord)
        obj.delete()

    def test_scrapping_record_value(self):
        self.assertEqual(self.scrap_line.scrapped_value, 10)

    def test_create_scrapping_record_line(self):
        obj = models.InventoryScrappingRecordLine.objects.create(
            product=self.product,
            quantity=1,
            scrapping_record=self.scrap
        )
        self.assertIsInstance(obj, models.InventoryScrappingRecordLine)
        obj.delete() 

    def test_scrapped_items(self):
        self.assertEqual(self.scrap.scrapped_items.count(), 1)

    def test_scrapped_value(self):
        self.assertEqual(self.scrap.scrapping_value, 10)
    
    def test_scrapping_record_scrap(self):
        prev_quantity = self.warehouse_item.quantity
        self.scrap.scrap()
        self.assertEqual(models.WareHouseItem.objects.first().quantity, 
            prev_quantity - 1)
        self.warehouse_item.increment(1)


class ItemModelTests(TestCase):
    fixtures = ['common.json', 'employees.json','inventory.json','accounts.json', 'journals.json', 'invoicing.json']

    @classmethod
    def setUpTestData(cls):
        create_test_inventory_models(cls)
        cls.inv = SalesInvoice.objects.create(
            status='sent',
            customer=Customer.objects.first(),
            )
        cls.line = SalesInvoiceLine.objects.create(
            product=cls.product,
            quantity=1,
            invoice=cls.inv,
        )
    
    def test_create_product(self):
        obj = models.Product.objects.create(
            name='other test name',
            unit=self.unit,
            pricing_method=1,
            direct_price=10,
            margin=0.25,
            unit_purchase_price=8,
            description='Test Description',
            supplier = self.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = self.category
        ) 
        self.assertIsInstance(obj, models.Product)
        obj.delete()
        #and associated functions

    def test_product_quantity(self):
        self.assertEqual(self.product.quantity, 9)

    def test_product_unit_sales_price(self):
        self.assertEqual(self.product.unit_sales_price, 10)

    def test_product_stock_value(self):
        self.assertEqual(self.product.stock_value, 10)

    def test_sales_to_date(self):
        self.assertEqual(self.product.sales_to_date, 10)


    def test_product_events(self):
        self.assertEqual(len(self.product.events), 1)

    def test_create_equipment(self):
        obj = models.Equipment.objects.create(
            name='test equipment',
            unit=self.unit,
            unit_purchase_price=10,
            description='Test Description',
            supplier = self.supplier,
            category = self.category,
            condition = "excellent",
            asset_data = self.asset
        )
        self.assertIsInstance(obj, models.Equipment)
        obj.delete()

    


    def test_create_raw_material(self):
        obj = models.RawMaterial.objects.create(
            name='test raw material',
            unit=self.unit,
            unit_purchase_price=10,
            description='Test Description',
            supplier = self.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = self.category
        )
        self.assertIsInstance(obj, models.RawMaterial)
        obj.delete()


    def test_create_consumable(self):
        obj = models.Consumable.objects.create(
            name='test comsumable',
            unit=self.unit,
            unit_purchase_price=10,
            description='Test Description',
            supplier = self.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = self.category
        )
        self.assertIsInstance(obj, models.Consumable)
        obj.delete()

class WarehouseModelTests(TestCase):
    fixtures = ['common.json', 'employees.json','inventory.json','accounts.json', 'journals.json',]

    @classmethod
    def setUpTestData(cls):
        create_test_inventory_models(cls)
        
    def tearDown(self):
        self.warehouse_item.quantity = 10 
        self.warehouse_item.save()


    def test_create_warehouse(self):
        obj = models.WareHouse.objects.create(
            name="Test Name",
            address="Test address",
            description="test description",
            inventory_controller=Employee.objects.first()
        )
        self.assertIsInstance(obj, models.WareHouse)
        obj.delete()

    def test_warehouse_item_count(self):
        self.assertEqual(self.warehouse.item_count, 1)

    def test_warehouse_total_item_quantity(self):
        self.assertEqual(self.warehouse.total_item_quantity, 9)

    def test_warehouse_all_items(self):
        self.assertEqual(self.warehouse.all_items.count(), 1)

    def test_warehouse_get_item(self):
        self.assertIsInstance(self.warehouse.get_item(self.product),
            models.WareHouseItem)

    def test_warehouse_decrement_item(self):
        prev_quantity =  models.WareHouseItem.objects.get(
            product=self.product).quantity
        self.warehouse.decrement_item(self.product, 1)
        self.assertEqual(models.WareHouseItem.objects.get(
            product=self.product).quantity,
            prev_quantity - 1)
        
        
    
    def test_warehouse_has_item(self):
        self.assertFalse(self.warehouse.has_item(self.equipment))
        self.assertTrue(self.warehouse.has_item(self.product))

    def test_warehouse_add_item(self):
        self.warehouse.add_item(self.equipment, 1)
        obj = models.WareHouseItem.objects.get(equipment=self.equipment)
        self.assertIsInstance(obj, models.WareHouseItem)
        
        obj.delete()

    def test_warehouse_transfer(self):
        dest = models.WareHouse.objects.create(
            name="Test destination",
            address='elsewhere'
        )
        self.warehouse.transfer(dest, self.product, 1)
        obj = models.WareHouseItem.objects.get(warehouse=dest, 
            product=self.product)
        self.assertIsInstance(obj, models.WareHouseItem)

        
        obj.delete()

    def test_create_warehouse_item(self):
        obj = models.WareHouseItem.objects.create(
            item_type=1,
            product=self.product,
            quantity=10,
            warehouse=self.warehouse,
        )
        self.assertIsInstance(obj, models.WareHouseItem)
        obj.delete()

    def test_warehouse_item_increment(self):
        prev_quantity = self.warehouse_item.quantity
        self.warehouse_item.increment(1)
        self.assertEqual(self.warehouse_item.quantity, 
            prev_quantity + 1)
    
    def test_warehouse_item_decrement(self):
        prev_quantity = self.warehouse_item.quantity
        self.warehouse_item.decrement(1)
        self.assertEqual(self.warehouse_item.quantity, 
            prev_quantity - 1)
    
    def test_warehouse_item_item(self):
        self.assertIsInstance(self.warehouse_item.item, models.Product)

    def test_warehouse_item_name(self):
        self.assertEqual(self.warehouse_item.name, 'test name')

    def test_create_storage_media(self):
        obj = models.StorageMedia.objects.create(
            name="Test Medium",
            warehouse=self.warehouse,
            description="shelves",
            unit=self.unit
        )
        self.assertIsInstance(obj, models.StorageMedia)
        obj.delete()

    def test_storage_media_contents(self):
        self.assertEqual(self.medium.contents.count(), 1)

    def test_storage_media_children(self):
        self.assertEqual(self.medium.children.count(), 0)

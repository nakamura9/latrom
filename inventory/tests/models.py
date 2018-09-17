import json
import urllib
import datetime
from django.utils import timezone
from common_data.tests import create_test_user, create_account_models

from django.test import TestCase,Client
from django.urls import reverse
from inventory import models 
from accounting.models import Account, JournalEntry

from common_data.models import Organization
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
            unit_purchase_price=8,
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
    cls.warehouse_item = models.WareHouseItem.objects.create(
        product = cls.product,
        item_type=1,
        quantity =10,
        warehouse = cls.warehouse
    )
    cls.order = models.Order.objects.create(
            expected_receipt_date = TODAY,
            issue_date = TODAY,
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
            quantity=10,
            order_price=1,
        )
    cls.stock_receipt = models.StockReceipt.objects.create(
            order = cls.order,
            receive_date = TODAY,
            note = 'Test Note',
            fully_received=True,
        )


class ModelTests(TestCase):
    fixtures = ['accounts.json', 'journals.json']

    @classmethod
    def setUpTestData(cls):
        super(ModelTests, cls).setUpTestData()
        create_test_inventory_models(cls)

    def test_create_supplier(self):
        sup = models.Supplier.objects.create(
            organization=self.organization,
            account = self.account_c
        )
        self.assertIsInstance(sup, models.Supplier)

    def test_create_product(self):
        product = models.Product.objects.create(
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
        self.assertIsInstance(product, models.Product)
        #and associated functions

    def test_create_order(self):
        ord = models.Order.objects.create(
            expected_receipt_date = TODAY,
            issue_date = TODAY,
            type_of_order=1,
            supplier=self.supplier,
            bill_to = 'Test Bill to',
            ship_to = self.warehouse,
            tracking_number = '34234',
            notes = 'Test Note',
            status = 'submitted'    
        )
        models.OrderItem.objects.create(
            order=ord,
            product=self.product,
            quantity=1,
        )
        self.assertIsInstance(ord, models.Order)
        #NB No transactions are created as yet

    def test_create_order_item(self):
        ord_item = models.OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=10,
            order_price=10
        )
        self.assertIsInstance(ord_item, models.OrderItem)

    def test_create_unit(self):
        unit = models.UnitOfMeasure.objects.create(
            name='Test Unit',
            description='Test description'
        )   
        self.assertIsInstance(unit, models.UnitOfMeasure)

    def test_create_stock_receipt(self):
        src = models.StockReceipt.objects.create(
            order = self.order,
            receive_date = TODAY,
            note = 'Test Note',
            fully_received=True,
        )
        self.assertIsInstance(src, models.StockReceipt)

    def test_create_category(self):
        cat = models.Category.objects.create(
            name='Test Category',
            description='Test Description'
        )
        self.assertIsInstance(cat, models.Category)

    def test_item_sales_to_date(self):
        #measure the number of items sold in entire history
        pass

    def test_item_stock_value(self):
        #needs a much more complex test!
        self.assertEqual(int(self.product.stock_value), 100)

    '''
    def test_item_increment_and_decrement(self):
        self.assertEqual(self.warehouse_item.increment(10), 20)
        self.assertEqual(self.item.decrement(10), 10)
    '''

    def test_order_total(self):
        #10 items @ $8 
        self.assertEqual(self.order.total, 80)

    def test_order_fully_received(self):
        self.assertFalse(self.order.fully_received)

    def test_order_percent_received(self):
        self.assertEqual(self.order.percent_received, 0)

    def test_order_receive(self):
        self.order.receive()
        self.assertTrue(self.order.fully_received)

        #break down changes
        models.StockReceipt.objects.latest('pk').delete()
        for item in self.order.orderitem_set.all():
            item.received = 0
            item.save()

    def test_order_item_fully_received(self):
        self.order_item.received = 10
        self.assertTrue(self.order_item.fully_received)
        
        #roll back changes
        self.order_item.received = 0
        self.order_item.save()

    def test_order_item_receive(self):
        self.order_item.receive(10)
        self.assertTrue(self.order_item.fully_received)
        
        #roll back changes
        self.order_item.received = 0
        self.order_item.save()

    def test_order_item_subtotal(self):
        #10 items @ $8
        self.assertEqual(self.order_item.subtotal, 80)
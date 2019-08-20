from common_data.tests.model_util import CommonModelCreator
from common_data.tests.accounts import create_accounts
from employees.tests.model_util import EmployeeModelCreator
from inventory import models 
import datetime

#change order status from order
class InventoryModelCreator():
    def __init__(self, klass):
        self.cls = klass

    def create_all(self):
        self.create_supplier()
        self.create_warehouse()
        self.create_order()
        self.create_unit()
        self.create_inventory_category()
        self.create_product_component()
        self.create_product()
        self.create_warehouse_item()
        self.create_orderitem()
        self.create_debit_note()

    def create_supplier(self):
        if not hasattr(self.cls, 'organization'):
            CommonModelCreator(self.cls).create_organization()
        
        if not hasattr(self.cls, 'account_c'):
            create_accounts(self.cls)

        self.cls.supplier = models.Supplier.objects.create(
            organization=self.cls.organization,
            account = self.cls.account_c
            )

        return self.cls.supplier


    def create_unit(self):
        self.cls.unit = models.UnitOfMeasure.objects.create(
            name='Test Unit',
            description='Test description'
        )
        return self.cls.unit

    def create_inventory_category(self):
        self.cls.inventory_category = models.Category.objects.create(
            name='Test Category',
            description='Test description'
        )
        return self.cls.inventory_category

    def create_product_component(self):
        self.cls.product_component = models.ProductComponent.objects.create(
            pricing_method=0, #KISS direct pricing
            direct_price=10,
            margin=0.5,
        )
        return self.cls.product_component 


    def create_product(self):
        if hasattr(self.cls, 'product'):
            return self.cls.product
        
        if not hasattr(self.cls, 'product_component'):
            self.create_product_component()
        
        if not hasattr(self.cls, 'unit'):
            self.create_unit()

        if not hasattr(self.cls, 'inventory_category'):
            self.create_inventory_category()
        
        if not hasattr(self.cls, 'supplier'):
            self.create_supplier()
        self.cls.product = models.InventoryItem.objects.create(
            name='test name',
            unit=self.cls.unit,
            type=0,
            unit_purchase_price=10,
            description='Test Description',
            supplier = self.cls.supplier,
            minimum_order_level = 0,
            maximum_stock_level = 20,
            category = self.cls.inventory_category,
            product_component = self.cls.product_component
        )

        return self.cls.product

    def create_warehouse(self):
        if hasattr(self.cls, 'warehouse'):
            return self.cls.warehouse

        self.cls.warehouse = models.WareHouse.objects.create(
            name="warehouse",
            address='location'
        )

    def create_warehouse_item(self):
        if hasattr(self.cls, 'warehouse_item'):
            return self.cls.warehouse_item

        if not hasattr(self.cls, 'product'):
            self.create_product()

        if not hasattr(self.cls, 'warehouse'):
            self.create_warehouse()

        self.cls.warehouse_item = models.WareHouseItem.objects.create(
            item=self.cls.product,
            quantity=10,
            warehouse=self.cls.warehouse
        )

    def create_order(self):
        if hasattr(self.cls, 'order'):
            return self.cls.order

        if not hasattr(self.cls, 'supplier'):
            self.create_supplier()

        if not hasattr(self.cls, 'warehouse'):
            self.create_warehouse()

        if not hasattr(self.cls, 'controller'):
            self.create_inventory_controller()

        self.cls.order = models.Order.objects.create(
            expected_receipt_date = datetime.date.today(),
            date = datetime.date.today(),
            supplier=self.cls.supplier,
            bill_to = 'Test Bill to',
            ship_to = self.cls.warehouse,
            tracking_number = '34234',
            notes = 'Test Note',
            status = 'draft',
            issuing_inventory_controller=self.cls.controller
        )

    def create_orderitem(self):
        if hasattr(self.cls, 'orderitem'):
            return self.cls.orderitem

        if not hasattr(self.cls, 'order'):
            self.create_order()

        if not hasattr(self.cls, 'product'):
            self.cls.create_product()

        self.cls.orderitem = models.OrderItem.objects.create(
            order=self.cls.order,
            item=self.cls.product,
            quantity=1,
            order_price=10,
        )

    def create_debit_note(self):
        if not hasattr(self.cls, 'order'):
            self.create_order()
            self.create_orderitem()

        self.cls.debit_note = models.DebitNote.objects.create(
            date=datetime.date.today(),
            order=self.cls.order,
            comments='Comment'
        )

    def create_inventory_controller(self):
        if hasattr(self.cls, 'controller'):
            return self.cls.controller
        if not hasattr(self.cls, 'employee'):
            EmployeeModelCreator(self.cls).create_employee()

        self.cls.controller = models.InventoryController.objects.create(
            employee=self.cls.employee
        )
        return self.cls.controller
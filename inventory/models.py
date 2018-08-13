# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from decimal import Decimal as D
import rest_framework

from django.db import models
from django.db.models import Q
from django.conf import settings
from accounting.models import JournalEntry, Journal, Account
from common_data.models import SingletonModel

class InventorySettings(SingletonModel):
    INVENTORY_VALUATION_METHODS = [
        (1, 'Averaging'),
        (2, 'FIFO'),
        (3, 'LIFO'),
        (4, 'Last order price')
    ]
    PRICING_METHODS = [
        (1, 'Direct Pricing'),
        (2, 'Margin'),
        (3, 'Markup')
    ]
    DOCUMENT_THEME_CHOICES = [
        (1, 'Simple'),
        (2, 'Blue'),
        (3, 'Steel'),
        (4, 'Verdant'),
        (5, 'Warm')
    ]
    INVENTORY_CHECK_FREQUENCY = [
        (1, 'Monthly'),
        (2, 'Quarterly'),
        (3, 'Bi-Annually'),
        (4, 'Annually')
    ]
    INVENTORY_CHECK_DATE = [
        (i, i) for i in range(28, 1)
    ]
    inventory_valuation_method = models.PositiveSmallIntegerField(
        choices = INVENTORY_VALUATION_METHODS, default=1
    )
    item_sales_pricing_method= models.PositiveSmallIntegerField(
        choices=PRICING_METHODS, default=1
    )
    order_template_theme = models.PositiveSmallIntegerField(
        choices=DOCUMENT_THEME_CHOICES, default=1
    )
    inventory_check_frequency = models.PositiveSmallIntegerField(
        choices=INVENTORY_CHECK_FREQUENCY, default=1
    )
    inventory_check_date = models.PositiveSmallIntegerField(
        choices=INVENTORY_CHECK_DATE, default=1
    )

class InventoryController(models.Model):
    '''Model that represents employees with the role of 
    inventory controller and have the ability to make purchase orders,
    receive them, transfer inventory between warehouses and perform other 
    functions.'''
    employee = models.ForeignKey('employees.Employee')


class Supplier(models.Model):
    '''The businesses and individuals that provide the organization with 
    products it will sell. Basic features include contact details address and 
    contact people.
    The account of the supplier is for instances when orders are made on credit.'''
    # one or the other 
    organization = models.OneToOneField('common_data.Organization', null=True)
    individual = models.OneToOneField('common_data.Individual', null=True)
    active = models.BooleanField(default=True)
    account = models.ForeignKey('accounting.Account',blank=True, null=True)

    @property
    def name(self):
        if self.organization:
            return self.organization.legal_name
        else:
            return self.individual.full_name

    @property
    def is_organization(self):
        return self.organization != None

    @property
    def supplier_email(self):
        if self.is_organization:
            return self.organization.email
        else:
            return self.individual.email

        
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk is None:
            n_suppliers = Supplier.objects.all().count()
            #will overwrite if error occurs
            self.account = Account.objects.create(
                name= "Supplier: %s" % self.name,
                id = 2100 + n_suppliers,
                balance =0,
                type = 'liability',
                description = 'Account which represents debt owed to a supplier',
                balance_sheet_category='current-liabilities'
            )
        
        super(Supplier, self).save(*args, **kwargs)
        



class Item(models.Model):
    '''The most basic element of inventory. Represents tangible products that are sold.
    this model tracks details concerning sale and receipt of products as well as their 
    value and pricing.
    
    methods
    ----------
    increment - increases the stock of the item.
    decrement - decreases the stock of the item.

    properties
    -----------
    stock_value - returns the value of the stock on hand in the inventory
        based on a valuation rule.
    events - returns representations of all the inventory movements by date and 
    description in the last 30 days
    
    '''
    PRICING_CHOICES = [
    (0, 'Manual'),
    (1, 'Margin'),
    (2, 'Markup')
]
    item_name = models.CharField(max_length = 32)
    code = models.AutoField(primary_key=True)
    unit = models.ForeignKey('inventory.UnitOfMeasure', blank=True, default=1)
    sku = models.CharField(max_length=16, blank=True)
    pricing_method = models.IntegerField(choices=PRICING_CHOICES, default=0)
    direct_price = models.DecimalField(max_digits=9, decimal_places=2)
    margin = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    markup = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    unit_purchase_price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True, default="")
    supplier = models.ForeignKey("inventory.Supplier", blank=True, null=True)
    image = models.FileField(blank=True, null=True, upload_to=settings.MEDIA_ROOT)
    minimum_order_level = models.IntegerField( default=0)
    maximum_stock_level = models.IntegerField(default=0)
    category = models.ForeignKey('inventory.Category', blank=True, null=True)
    sub_category = models.ForeignKey('inventory.Category', 
       related_name='sub_category', blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.code) + " - " + self.item_name

    @property
    def quantity(self):
        #returns quantity from all warehouses
        items = WareHouseItem.objects.filter(item=self)
        return reduce(lambda x, y: x + y, [i.quantity for i in items], 0)
    
    @property
    def unit_sales_price(self):
        if self.pricing_method == 0:
            return self.direct_price
        elif self.pricing_method == 1:
            return D(self.unit_purchase_price / (1 - self.margin))
        else:
            return D(self.unit_purchase_price * (1 + self.markup))
    
    @property
    def stock_value(self):
        '''all calculations are based on the last 30 days
        currently implementing the options of fifo and averaging.
        fifo - first in first out, measure the value of the items 
        based on the price they were bought assuming the remaining items 
        are the last ones bought.
        averaging- calculating the overall stock value on the average of all
        the values during the period under consderation.
        '''
        return 0

        #dates under consideration 
        TODAY  = datetime.date.today()
        START = TODAY - datetime.timedelta(days=30)
        
        #get the most recent price older than 30 days
        older_items = OrderItem.objects.filter(
            Q(item=self) 
            & Q(received__gt = 0)
            & Q(order__issue_date__lt = START))

        if older_items.count() > 0:
            previous_price = older_items.latest('order__issue_date').order_price
        else:
            #uses the oldest available price. not implemented here
            previous_price = self.unit_purchase_price
         
        # get the ordered items from the last 30 days.
        ordered_in_last_month = OrderItem.objects.filter(
            Q(item=self) 
            & Q(received__gt = 0)
            & Q(order__issue_date__gte = START)
            & Q(order__issue_date__lte =TODAY))

        #calculate the number of items ordered in the last 30 days
        ordered_quantity = reduce(lambda x, y: x + y, 
            [i.received for i in ordered_in_last_month], 0)
        
        #get the value of items ordered in the last month
        total_ordered_value = reduce(lambda x,y: x + y,
            [i.received_total for i in ordered_in_last_month], 0)
        
        #get the number of sold items in the last 30 days
        sold_in_last_month = None
        #calculate the number of items sold in that period
        sold_quantity = reduce(lambda x, y: x + y, 
            [i.quantity for i in sold_in_last_month], 0)

        #get the value of the items sold in the last month
        total_sold_value = reduce(lambda x, y: x + y, 
            [i.total_without_discount for i in sold_in_last_month], 0)
        
        #determine the quantity of inventory before the valuation period
        initial_quantity = self.quantity + ordered_quantity - sold_quantity
        
        # get the value of the items before the valuation period
        initial_value = D(initial_quantity) * previous_price
        total_value = 0
        
        #if no valuation system is being used
        #create inventory config ***
        if not config.get('inventory_valuation', None):
            return self.unit_sales_price * D(self.quantity)
        else:
            if config['inventory_valuation'] == 'averaging':
                total_value += initial_value
                total_value += total_ordered_value

                average_value = total_value / (ordered_quantity + initial_quantity)
                return average_value 


            elif config['inventory_valuation'] == 'fifo':
                # while loop compares the quantity sold with the intial inventory,
                # and the new inventory after each new order.
                ordered_in_last_month_ordered = list(ordered_in_last_month.order_by(
                    'order__issue_date'))
                quantity = initial_quantity
                index = 0
                while quantity < sold_quantity:
                    quantity += ordered_in_last_month_ordered[index]
                    index += 1

                if index == 0:
                    total_value += initial_value - total_sold_value
                    total_value += total_ordered_value
                    average_value = total_value / D(ordered_quantity + (initial_quantity - sold_quantity))
                    return average_value
                else:
                    remaining_orders = ordered_in_last_month_ordered[index:]
                    total_value = 0
                    for i in remaining_orders:
                        total_value += i.order_price * i.received
                    average_value = total_value / reduce(lambda x,y: x + y, 
                        [i.received for i in remaining_orders], 0)

            else:
                return self.unit_sales_price * D(self.quantity)

    @property
    def sales_to_date(self):
        return 0 #!!fix
        items = InvoiceItem.objects.filter(item=self)
        total_sales = reduce(lambda x,y: x + y, [item.quantity * item.price for item in items], 0)
        return total_sales
    
    def delete(self):
        self.active = False
        self.save()

    @property
    def events(self):
        class Event:
            def __init__(self, date, description):
                self.date = date
                self.description= description

            def __lt__(self, other):
                return other.date < self.date
        # 30 day limit on event retrieval.
        epoch = datetime.date.today() - datetime.timedelta(days=30)

        #from invoices
        items= []
        #fix 
        '''[Event(i.invoice.due_date, 
            "removed %d items from inventory as part of invoice #%d." % (i.quantity, i.invoice.pk)) \
                for i in InvoiceItem.objects.filter(Q(item=self) 
                    & Q(invoice__date_issued__gte= epoch))]
        '''
        # from orders
        orders = [Event(o.order.issue_date, 
            "added %d items to inventory from purchase order #%d." % (o.received, o.order.pk)) \
                for o in OrderItem.objects.filter(Q(item=self) 
                    & Q(order__issue_date__gte= epoch)) if o.received > 0]

        events = items + orders 
        return sorted(events)

class Order(models.Model):
    '''The record of all purchase orders for inventory of items that 
    will eventually be sold. Contains the necessary data to update 
    inventory and update the Purchases Journal.
    An aggregate with the OrderItem class.
    A cash order creates a transaction creation.
    A deferred payment pays on the deferred date.(Not yet implemented)
    A pay on receipt order creates the transaction when receiving a 
    goods received voucher.

    properties
    ------------
    total - returns the total value of the items ordered.
    received_total - returns the numerical value of items received
    fully_received - returns a boolean if all the ordered items have 
        been received.
    percent_received - is the percentage of the order that has been
        fulfilled by the supplier.
    
    methods
    -------------
    receive - quickly generates a stock receipt where all items are 
        marked fully received 
    '''
    ORDER_TYPE_CHOICES = [
        (0, 'Cash Order'),
        (1, 'Deffered Payment Order'),
        (2, 'Pay on Receipt') ]
    
    expected_receipt_date = models.DateField()
    issue_date = models.DateField()
    type_of_order = models.IntegerField(choices=ORDER_TYPE_CHOICES, default=0)
    deferred_date = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey('inventory.supplier', blank=True, null=True)
    supplier_invoice_number = models.CharField(max_length=32, blank=True, default="")
    bill_to = models.CharField(max_length=128, blank=True, default="")
    ship_to = models.ForeignKey('inventory.WareHouse')
    tax = models.ForeignKey('accounting.Tax', default=1)
    tracking_number = models.CharField(max_length=64, blank=True, default="")
    notes = models.TextField()
    status = models.CharField(max_length=24, choices=[
        ('received-partially', 'Partially Received'),
        ('received', 'Received in Total'),
        ('draft', 'Internal Draft'),
        ('submitted', 'Submitted to Supplier')
    ])
    active = models.BooleanField(default=True)
    received_to_date = models.FloatField(default=0.0)
    
    def __str__(self):
        return 'ORD' + str(self.pk)

    @property
    def items(self):
        return self.orderitem_set.all()

    @property
    def total(self):
        return reduce(lambda x, y: x + y , [item.subtotal for item in self.items], 0)

    @property
    def subtotal(self):
        return self.total - self.tax_amount

    @property
    def tax_amount(self):
        if self.tax:
            return self.total * (D(self.tax.rate) / D(100))
        return D(0.0)
    
    @property
    def received_total(self):
        return reduce(lambda x, y: x + y , [item.received_total for item in self.items], 0)
    
    @property
    def fully_received(self):
        for item in self.items:
            if item.fully_received == False : return False
        return True

    @property
    def percent_received(self):
        items = self.orderitem_set.all()
        n_items = items.count()
        received = 0
        for item in items:
            if item.fully_received == True : 
                received += 1
        return (float(received) / float(n_items)) * 100.0

    def create_deffered_entry(self):
        j = JournalEntry.objects.create(
                    reference = "Auto generated entry created by order " + str(self),
                    date=self.deferred_date,
                    memo = self.notes,
                    journal = Journal.objects.get(pk=4)
                )
        j.credit(self.subtotal, Account.objects.get(pk=2000))#accounts payable
        j.debit(self.total, self.supplier.account) # since we owe the supplier
        j.credit(self.tax_amount, Account.objects.get(pk=2001))#sales tax

    def create_immediate_entry(self):
        j = JournalEntry.objects.create(
                date = self.issue_date,
                reference = "Auto generated entry from order" + str(self),
                memo=self.notes,
                journal = Journal.objects.get(pk=4)
            )
        j.credit(self.subtotal, Account.objects.get(pk=1004))#inventory
        j.debit(self.total, Account.objects.get(pk=4006))#purchases account
        j.credit(self.tax_amount, Account.objects.get(pk=2001))#sales tax

    def receive(self):
        if self.status != 'received':
            sr = StockReceipt.objects.create(
                    order=self,
                    receive_date= datetime.date.today(),
                    note = 'Autogenerated receipt from order number' + \
                        str(self.pk),
                    fully_received=True
                )
            for item in self.orderitem_set.all():
                item.receive(item.quantity)
            sr.create_entry()
    #check for deffered date with deferred type of invoice

class OrderItem(models.Model):
    '''A component of an order this tracks the order price 
    of an item its quantity and how much has been received.
    
    methods
    -----------
    receive - takes a number and adds its value to the item inventory
        and the orderitem's received quantity field.
    
    properties
    -----------
    received_total - returns the cash value of the items received
    subtotal - returns the cash value of the items ordered
    '''
    order = models.ForeignKey('inventory.Order')
    item = models.ForeignKey('inventory.item')
    quantity = models.FloatField()
    order_price = models.DecimalField(max_digits=6, decimal_places=2)
    received = models.FloatField(default=0.0)

    @property
    def fully_received(self):
        if self.received < self.quantity:
            return False
        return True

    def receive(self, n):
        n= float(n)
        self.received += n
        
        if not self.order.ship_to.has_item(self.item):
            #item does not yet exist
            wh_item = WareHouseItem.objects.create(item=self.item,
                quantity = n,
                warehouse=self.order.ship_to)
        else:
            wh_item = WareHouseItem.objects.get(warehouse=self.order.ship_to, 
            item= self.item)
            wh_item.increment(n)

        self.item.unit_purchase_price = self.order_price
        self.item.save()
        self.save()
        
    def __str__(self):
        return str(self.item) + ' -' + str(self.order_price)

    def save(self, *args, **kwargs):
        if not self.order_price:
            self.order_price = self.item.unit_purchase_price
        else:
            self.item.unit_purchase_price = self.order_price
            self.item.save()
        super(OrderItem, self).save(*args, **kwargs)
        
    @property
    def received_total(self):
        return D(self.received)  * self.order_price

    @property
    def subtotal(self):
        return D(self.quantity) * self.order_price

class UnitOfMeasure(models.Model):
    '''Class for arepresenting units of inventory.
    can be a base unit where no calculations are required.
    can also be a derived unit where the quantity is calculated back into the base unit for each element.'''
    name = models.CharField(max_length=64)
    description = models.TextField(default="")
    is_derived = models.BooleanField(default = False)
    base_unit = models.ForeignKey('inventory.UnitOfMeasure', null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DerivedUnitStage(models.Model):
    OPERATIONS = [
        (0, 'sum'),
        (1, 'difference'),
        (2, 'product'),
        (3, 'ratio')
        ]
    stage_number = models.PositiveSmallIntegerField()
    operation = models.PositiveSmallIntegerField(choices=OPERATIONS)
    value = models.FloatField()
    unit = models.ForeignKey('inventory.UnitOfMeasure')

class Category(models.Model):
    '''Used to organize inventory'''
    name = models.CharField(max_length=64)
    parent = models.ForeignKey('inventory.Category', blank=True, null=True)
    description = models.TextField(default="")

    def __str__(self):
        return self.name

class StockReceipt(models.Model):
    '''
    Part of the inventory ordering workflow.
    When an order is generated this object is created to verify 
    the receipt of items and comment on the condition of the 
    products.

    methods
    ---------
    create_entry - method only called for instances where inventory 
    is paid for on receipt as per order terms.
    '''
    order = models.ForeignKey('inventory.Order')
    received_by = models.ForeignKey('employees.Employee', 
        default=1)
    receive_date = models.DateField()
    note =models.TextField(blank=True, default="")
    fully_received = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + ' - ' + str(self.receive_date)

    def save(self, *args, **kwargs):
        super(StockReceipt, self).save(*args, **kwargs)
        self.order.received_to_date = self.order.received_total
        self.order.save()
        

    def create_entry(self):
        j = JournalEntry.objects.create(
            reference = "ORD" + str(self.order.pk),
            memo = "Auto generated Entry from Purchase Order",
            date =self.receive_date,
            journal = Journal.objects.get(pk=2)
        )
        new_total = self.order.received_total - D(self.order.received_to_date)
        j.simple_entry(
            new_total,
            Account.objects.get(pk=1004),#inventory
            Account.objects.get(pk=1000)#checking account
        )
        

class WareHouse(models.Model):
    name = models.CharField(max_length=128)
    address = models.TextField()
    
    @property
    def product_count(self):
        return self.all_items.count
    
    @property
    def item_count(self):
        return reduce(lambda x, y: x + y, 
            [i.quantity for i in self.all_items], 0)

    @property
    def all_items(self):
        return self.warehouseitem_set.all()

    def decrement_item(self, item, quantity):
        #safety checks handled elsewhere
        #created to avoid circular imports in invoices
        self.get_item(item).decrement(quantity)


    def has_item(self, item):
        return(
            WareHouseItem.objects.filter(item=item, warehouse=self).count() > 0
        ) 
            
    
    def get_item(self, item):
        if self.has_item(item):
            return WareHouseItem.objects.get(item=item, warehouse=self)
        else:
             return None
    
    def add_item(self, item, quantity):
        #check if record of item is already in warehouse
        if self.has_item(item):
            self.get_item(item).increment(quantity)
        else:
            self.warehouseitem_set.create(item=item, quantity=quantity)

    def transfer(self, other, item, quantity):
        #transfer stock from current warehouse to other warehouse
        
        if not other.has_item(item):
            raise Exception('The destination warehouse does not stock this item')
        elif not self.has_item(item):
            raise Exception('The source warehouse does not stock this item')

        else:
            other.get_item(item).increment(quantity)
            self.get_item(item).decrement(quantity)
            # for successful transfers, record the transfer cost some way

    def __str__(self):
        return self.name

class WareHouseItem(models.Model):
    item = models.ForeignKey('inventory.Item')
    quantity = models.FloatField()
    warehouse = models.ForeignKey('inventory.Warehouse', default=1)
    verified = models.BooleanField(default=False)
    #verification expires after the next inventory check date

    def increment(self, amt):
        amount = float(amt)
        if self.quantity + amount > self.item.maximum_stock_level:
            raise Exception('Stock level will exceed maximum allowed')
        self.quantity += amount
        self.save()
        return self.quantity

    def decrement(self, amt):
        amount = float(amt)
        print self.quantity
        print amount
        if self.quantity < amount:
            raise ValueError('Cannot have a quantity less than zero')
        self.quantity -= amount
        self.save()
        # check if min stock level is exceeded
        return self.quantity

#might need to rename
class InventoryCheck(models.Model):
    date = models.DateField()
    next_adjustment_date = models.DateField(null=True)#not required
    adjusted_by = models.ForeignKey('employees.Employee')
    warehouse = models.ForeignKey('inventory.WareHouse')
    comments = models.TextField()
    
    @property 
    def adjustments(self):
        return self.stockadjustment_set.all()

    @property
    def value_of_all_adjustments(self):
        return reduce(lambda x, y: x + y, 
            [i.adjustment_value for i in self.adjustments], 0)

class StockAdjustment(models.Model):
    warehouse_item = models.ForeignKey('inventory.WareHouseItem')
    adjustment = models.FloatField()
    note = models.TextField()
    inventory_check = models.ForeignKey('inventory.InventoryCheck')

    @property
    def adjustment_value(self):
        return D(self.adjustment) * self.warehouse_item.item.unit_purchase_price

    @property
    def prev_quantity(self):
        return self.warehouse_item.quantity + self.adjustment

    def adjust_inventory(self):
        self.warehouse_item.decrement(self.adjustment)

    def save(self, *args, **kwargs):
        super(StockAdjustment, self).save(*args, **kwargs)
        self.adjust_inventory()

class TransferOrder(models.Model):
    issue_date = models.DateField()
    expected_completion_date = models.DateField()
    issuing_inventory_controller = models.ForeignKey('employees.Employee',
        related_name='issuing_inventory_controller')
    receiving_inventory_controller = models.ForeignKey('employees.Employee', default=1)
    actual_completion_date =models.DateField(null=True)#provided later
    source_warehouse = models.ForeignKey('inventory.WareHouse',
        related_name='source_warehouse')
    receiving_warehouse = models.ForeignKey('inventory.WareHouse')
    order_issuing_notes = models.TextField(blank=True)
    receive_notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    
    #link expenses 
    def complete(self):
        for line in self.transferorderline_set.all():
            self.source_warehouse.decrement_item(line.item, line.quantity)
            self.receiving_warehouse.add_item(line.item, line.quantity)
        print 'called'
        self.completed = True
        self.save()

class TransferOrderLine(models.Model):
    item = models.ForeignKey('inventory.Item')
    quantity = models.FloatField()
    transfer_order = models.ForeignKey('inventory.TransferOrder')


class InventoryScrappingRecord(models.Model):
    date = models.DateField()
    controller = models.ForeignKey('inventory.InventoryController')
    warehouse = models.ForeignKey('inventory.WareHouse')
    comments = models.TextField(blank=True)


class InventoryScrappingRecordLine(models.Model):
    item = models.ForeignKey('inventory.Item')
    quantity = models.FloatField()
    scrapping_record = models.ForeignKey('inventory.InventoryScrappingRecord')


class StorageMedia(models.Model):
    name = models.CharField(max_length = 255)
    warehouse = models.ForeignKey('inventory.WareHouse')
    location = models.ForeignKey('inventory.StorageMedia', null=True, blank=True)
    description = models.TextField()
    unit = models.ForeignKey('inventory.UnitOfMeasure')
    length = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    capacity = models.FloatField(default=0.0)

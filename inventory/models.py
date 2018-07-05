# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import decimal

from django.db import models
from django.db.models import Q
from django.conf import settings
from invoicing.models import Invoice, InvoiceItem
from accounting.models import JournalEntry, Journal, Account
from common_data.utilities import load_config

class Supplier(models.Model):
    '''The businesses and individuals that provide the organization with 
    products it will sell. Basic features include contact details address and 
    contact people.
    The account of the supplier is for instances when orders are made on credit.'''
    name = models.CharField(max_length=64)
    contact_person = models.CharField(max_length=64, blank=True, default="")
    physical_address = models.CharField(max_length=128, blank=True, default="")
    telephone = models.CharField(max_length=16, blank=True, default="")
    email = models.EmailField(max_length=64, blank=True, default="")
    website = models.CharField(max_length=64, blank=True, default="")
    active = models.BooleanField(default=True)
    account = models.ForeignKey('accounting.Account', null=True)

    def __str__(self):
        return self.name

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
    item_name = models.CharField(max_length = 32)
    code = models.AutoField(primary_key=True)
    unit = models.ForeignKey('inventory.UnitOfMeasure', blank=True, default="")
    unit_sales_price = models.DecimalField(max_digits=6, decimal_places=2)
    unit_purchase_price = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField(blank=True, default="")
    supplier = models.ForeignKey("inventory.Supplier", blank=True, null=True)
    image = models.FileField(blank=True, null=True, upload_to=settings.MEDIA_ROOT)
    quantity = models.FloatField(blank=True, default=0)
    minimum_order_level = models.IntegerField( default=0)
    maximum_stock_level = models.IntegerField(default=0)
    category = models.ForeignKey('inventory.Category', blank=True, null=True)
    sub_category = models.ForeignKey('inventory.Category', 
       related_name='sub_category', blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.code) + " - " + self.item_name

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
        if self.quantity == 0:
            return 0

        config = load_config()
        #dates under consideration 
        TODAY  = datetime.date.today()
        START = TODAY - datetime.timedelta(days=30)
        
        #get the most recent price older than 30 days
        older_items = OrderItem.objects.filter(
            Q(item=self) 
            & Q(received__gt = 0)
            & Q(order__issue_date__lt = START))

        if older_items.count() > 0:
            previous_price = older_items.latest('issue_date').order_price
        else:
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
        total_ordered_value = 0
        for i in ordered_in_last_month:
            total_ordered_value += i.received * i.order_price

        #get the number of sold items in the last 30 days
        sold_in_last_month = InvoiceItem.objects.filter(
            Q(item=self)
            & Q(invoice__date_issued__gte = START)
            & Q(invoice__date_issued__lte =TODAY))

        #calculate the number of items sold in that period
        sold_quantity = reduce(lambda x, y: x + y, 
            [i.quantity for i in sold_in_last_month], 0)

        #get the value of the items sold in the last month
        total_sold_value = 0
        for i in sold_in_last_month:
            total_ordered_value += i.quantity * i.price

        #determine the quantity of inventory before the valuation period
        initial_quantity = self.quantity + ordered_quantity - sold_quantity
        
        # get the value of the items before the valuation period
        intial_value = decimal.Decimal(initial_quantity) * previous_price
        total_value = 0
        
        #if no valuation system is being used
        if not config.get('inventory_valuation', None):
            return self.unit_sales_price * decimal.Decimal(self.quantity)
        else:
            if config['inventory_valuation'] == 'averaging':
                total_value += intial_value
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
                    average_value = total_value / (ordered_quantity + (initial_quantity - sold_quantity))
                    return average_value
                else:
                    remaining_orders = ordered_in_last_month_ordered[index:]
                    total_value = 0
                    for i in remaining_orders:
                        total_value += i.order_price * i.received
                    average_value = total_value / reduce(lambda x,y: x + y, 
                        [i.received for i in remaining_orders], 0)

            else:
                return self.unit_sales_price * decimal.Decimal(self.quantity)

    @property
    def sales_to_date(self):
        items = InvoiceItem.objects.filter(item=self)
        total_sales = reduce(lambda x,y: x + y, [item.quantity * item.price for item in items], 0)
        return total_sales
    
    def increment(self, amount):
        self.quantity += float(amount)
        self.save()
        return self.quantity

    def decrement(self, amount):
        self.quantity -= float(amount)
        self.save()
        return self.quantity
    
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
        items= [Event(i.invoice.due_date, 
            "removed %d items from inventory as part of invoice #%d." % (i.quantity, i.invoice.pk)) \
                for i in InvoiceItem.objects.filter(Q(item=self) 
                    & Q(invoice__date_issued__gte= epoch))]
        
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
    
    expected_receipt_date = models.DateField()
    issue_date = models.DateField()
    type_of_order = models.IntegerField(choices=[
        (0, 'Cash Order'),
        (1, 'Deffered Payment Order'),
        (2, 'Pay on Receipt') ], default=0)
    deferred_date = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey('inventory.supplier', blank=True, null=True)
    bill_to = models.CharField(max_length=128, blank=True, default="")
    ship_to = models.CharField(max_length=128, blank=True, default="")
    tracking_number = models.CharField(max_length=64, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    status = models.CharField(max_length=16, choices=[
        ('received', 'Received'),
        ('draft', 'Draft'),
        ('submitted', 'Submitted')
    ])
    active = models.BooleanField(default=True)
    received_to_date = models.FloatField(default=0.0)
    
    def __str__(self):
        return 'ORD' + str(self.pk)

    @property
    def total(self):
        return reduce(lambda x, y: x + y , [item.subtotal for item in self.orderitem_set.all()], 0)

    @property
    def received_total(self):
        return reduce(lambda x, y: x + y , [item.received_total for item in self.orderitem_set.all()], 0)
    
    @property
    def fully_received(self):
        for item in self.orderitem_set.all():
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
        return (float(received) / float(n_items)) * 100

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

    def save(self, *args, **kwargs):
        super(Order, self).save(*args, **kwargs)
        if self.type_of_order == 1:
            if self.deferred_date == None:
                raise ValueError('The Order with a deferred payment must have a deferred payment date.')
            if self.supplier.account == None:
                raise ValueError('A deffered payment requires the organization to have an account with the supplier')
            else:
                #create transaction dated deferred date
                j = JournalEntry.objects.create(
                    reference = "Auto generated entry created by order " + str(self),
                    date=self.deferred_date,
                    memo = self.notes,
                    journal = Journal.objects.get(pk=4)
                )
                j.simple_entry(
                    self.total,
                    Account.objects.get(pk=2000), #accounts payable
                    self.supplier.account, # since we owe the supplier
                    
                )
        elif self.type_of_order == 0:
            j = JournalEntry.objects.create(
                date = self.issue_date,
                reference = "Auto generated entry from order" + str(self),
                memo=self.notes,
                journal = Journal.objects.get(pk=4)
            )
            j.simple_entry(
                self.total,
                Account.objects.get(pk=1004),#inventory
                Account.objects.get(pk=4006),#purchases account
            )
        else:
            #create no transaction until stock receipt
            pass

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
    order = models.ForeignKey('inventory.Order', null=True)
    item = models.ForeignKey('inventory.item', null=True)
    quantity = models.FloatField()
    #change and move this to the item
    #make changes to the react app as well
    order_price = models.DecimalField(max_digits=6, decimal_places=2)
    received = models.FloatField(default=0.0)

    @property
    def fully_received(self):
        if self.received < self.quantity:
            return False
        return True

    def receive(self, n):
        self.received += float(n)
        self.item.quantity += float(n)
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
        return decimal.Decimal(self.received)  * self.order_price

    @property
    def subtotal(self):
        return decimal.Decimal(self.quantity) * self.order_price

class UnitOfMeasure(models.Model):
    '''Simple class for representing units of inventory.'''
    name = models.CharField(max_length=64)
    description = models.TextField(default="")
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    '''Used to organize inventory'''
    name = models.CharField(max_length=64)
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
    order = models.ForeignKey('inventory.Order', null=True)# might make one to one
    receive_date = models.DateField()
    note =models.TextField(blank=True, default="")
    fully_received = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk) + ' - ' + str(self.receive_date)

    def save(self, *args, **kwargs):
        super(StockReceipt, self).save(*args, **kwargs)
        if self.order.type_of_order == 2:#payment on receipt
            self.create_entry()

    def create_entry(self):
        j = JournalEntry.objects.create(
            reference = "ORD" + str(self.order.pk),
            memo = "Auto generated Entry from Purchase Order",
            date =self.receive_date,
            journal = Journal.objects.get(pk=2)
        )
        new_total = self.order.received_total - decimal.Decimal(self.order.received_to_date)
        j.simple_entry(
            new_total,
            Account.objects.get(pk=1004),
            Account.objects.get(pk=1000)
        )
        self.order.received_to_date = self.order.received_total
        self.order.save()

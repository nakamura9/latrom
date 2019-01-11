# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal as D
from functools import reduce

import rest_framework
from django.conf import settings
from django.db import models
from django.db.models import Q

import inventory
from accounting.models import Account, Journal, JournalEntry
from common_data.models import SingletonModel, SoftDeletionModel

from .warehouse_models import StorageMedia, WareHouseItem


class Order(SoftDeletionModel):
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
    ORDER_STATUS_CHOICES = [
        ('received-partially', 'Partially Received'),
        ('received', 'Received in Total'),
        ('draft', 'Internal Draft'),
        ('submitted', 'Submitted to Supplier')
    ]
    
    expected_receipt_date = models.DateField()
    date = models.DateField()
    due = models.DateField(blank=True, null=True)
    supplier = models.ForeignKey('inventory.supplier', 
        on_delete=models.SET_NULL, null=True, default=1)
    supplier_invoice_number = models.CharField(max_length=32, 
        blank=True,  default="")
    bill_to = models.CharField(max_length=128, blank=True, 
        default="")
    ship_to = models.ForeignKey('inventory.WareHouse', 
        on_delete=models.SET_NULL, null=True)
    tax = models.ForeignKey('accounting.Tax',on_delete=models.SET_NULL, null=True, 
        default=1)
    tracking_number = models.CharField(max_length=64, blank=True, 
        default="")
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=24, 
        choices=ORDER_STATUS_CHOICES)
    received_to_date = models.FloatField(default=0.0)
    issuing_inventory_controller = models.ForeignKey('auth.user', 
        default=1, on_delete=models.SET_NULL, null=True)
    entry = models.ForeignKey('accounting.JournalEntry',
         blank=True, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return 'ORD' + str(self.pk)

    @property
    def items(self):
        return self.orderitem_set.all()

    @property
    def total(self):
        return self.subtotal + self.tax_amount
        

    @property
    def subtotal(self):
        return reduce(lambda x, y: x + y , [item.subtotal for item in self.items], 0)

    @property
    def tax_amount(self):
        if self.tax:
            return self.subtotal * (D(self.tax.rate) / D(100))
        return D(0.0)
    
    @property
    def payments(self):
        return OrderPayment.objects.filter(order=self)
    
    @property
    def payment_status(self):
        total_paid = reduce(lambda x, y: x + y.amount,  self.payments, 0)
        if total_paid >= self.total:
            return "paid"
        elif total_paid > 0 and total_paid < self.total:
            return "paid-partially"
        else:
            return "unpaid"

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

    def create_entry(self):
        #verified
        if not self.entry:
            j = JournalEntry.objects.create(
                    reference = "Auto generated entry created by order " + str(
                        self),
                    date=self.date,
                    memo = self.notes,
                    journal = Journal.objects.get(pk=4),
                    created_by = self.issuing_inventory_controller
                )

            #accounts payable
            # since we owe the supplier
            if not self.supplier:
                self.supplier.create_account()
            j.credit(self.total, self.supplier.account)
            j.debit(self.subtotal, Account.objects.get(pk=1004))
            j.debit(self.tax_amount, Account.objects.get(pk=2001))
        else:
            j = self.entry

        if not self.entry:
            self.entry = j
    
        
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
            self.status = 'received'
            self.save()

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
    ITEM_TYPE_CHOICES =[
        (1, 'Product'),
        (2, 'Consumable'),
        (3, 'Equipment'),
        (4, 'Raw Material')
        ]
    order = models.ForeignKey('inventory.Order', on_delete=models.SET_NULL, null=True, )
    item_type = models.PositiveSmallIntegerField(default=1, 
        choices=ITEM_TYPE_CHOICES)
    product = models.ForeignKey('inventory.product', on_delete=models.SET_NULL, null=True)
    consumable = models.ForeignKey('inventory.consumable', on_delete=models.SET_NULL, 
        null=True)
    equipment = models.ForeignKey('inventory.equipment', on_delete=models.SET_NULL,
        null=True)
    raw_material = models.ForeignKey('inventory.rawmaterial', on_delete=models.SET_NULL,
        null=True)
    quantity = models.FloatField()
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=models.SET_NULL, null=True, 
        default=1)
    order_price = models.DecimalField(max_digits=6, decimal_places=2)
    received = models.FloatField(default=0.0)

    def __init__(self, *args,**kwargs):
        super(OrderItem, self).__init__(*args, **kwargs)
        self.mapping = {
            1: self.product,
            2: self.consumable,
            3: self.equipment,
            4: self.raw_material
        }

    @property
    def item(self):
        return self.mapping[self.item_type]

    @property
    def fully_received(self):
        if self.received < self.quantity:
            return False
        return True

    def receive(self, n, medium=None):
        n= float(n)
        self.received += n
        
        wh_item = self.order.ship_to.add_item(self.item, n)
        if medium:
            medium = StorageMedia.objects.get(pk=medium)
            wh_item.location=medium
            wh_item.save()
        
        self.item.set_purchase_price(self.order_price)
            
        self.save()
        
    def __str__(self):
        return str(self.item) + ' -' + str(self.order_price)

        
    @property
    def received_total(self):
        '''The total value of the item as received'''
        return D(self.received)  * self.order_price

    @property
    def subtotal(self):
        '''The total value of the item as ordered, not received'''
        return D(self.quantity) * self.order_price


class OrderPayment(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=6,decimal_places=2)
    order = models.ForeignKey('inventory.order', on_delete=models.SET_NULL, null=True)
    comments = models.TextField()
    entry = models.ForeignKey('accounting.JournalEntry', on_delete=models.SET_NULL,
        blank=True, null=True)

    def create_entry(self, comments=""):
        j = JournalEntry.objects.create(
                reference='PMT' + str(self.pk),
                memo= 'Auto generated journal entry from order payment.' \
                    if comments == "" else comments,
                date=self.date,
                journal =Journal.objects.get(pk=4),
                created_by = self.order.issuing_inventory_controller
            )
        
        # split into sales tax and sales
        if not self.order.tax:
            j.simple_entry(
                self.amount,
                Account.objects.get(
                    pk=1000),#cash in checking account
                self.order.supplier.account,
            )
        else:
            tax_amount = self.amount * D(self.order.tax.rate / 100.0) 

            # will now work for partial payments
            j.debit(self.amount, self.order.supplier.account)
            # calculate tax as a proportion of the amount paid
            
            # purchases account
            j.credit(self.amount - tax_amount, Account.objects.get(pk=4006))
            # tax
            j.debit(tax_amount, Account.objects.get(pk=2001))

        if not self.entry:
            self.entry = j
            self.save()

#Note as currently designed it cannot be known when exactly an item entered inventory
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
    order = models.ForeignKey('inventory.Order', on_delete=models.SET_NULL, null=True)
    received_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True,
        default=1, limit_choices_to=Q(user__isnull=False))
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
        #verified
        j = JournalEntry.objects.create(
            reference = "ORD" + str(self.order.pk),
            memo = "Auto generated Entry from Purchase Order",
            date =self.receive_date,
            journal = Journal.objects.get(pk=2),
            created_by = self.received_by.user
        )
        new_total = self.order.received_total - D(self.order.received_to_date)
        j.simple_entry(
            new_total,
            Account.objects.get(pk=1004),#inventory
            self.order.supplier.account#checking account
        )

#might need to rename
class InventoryCheck(models.Model):
    date = models.DateField()
    next_adjustment_date = models.DateField(null=True, blank=True)#not required
    adjusted_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, limit_choices_to=Q(user__isnull=False) )
    warehouse = models.ForeignKey('inventory.WareHouse', on_delete=models.SET_NULL, null=True )
    comments = models.TextField()
    
    @property 
    def adjustments(self):
        return self.stockadjustment_set.all()

    @property
    def value_of_all_adjustments(self):
        return reduce(lambda x, y: x + y, 
            [i.adjustment_value for i in self.adjustments], 0)

class StockAdjustment(models.Model):
    warehouse_item = models.ForeignKey('inventory.WareHouseItem', on_delete=models.SET_NULL, null=True)
    adjustment = models.FloatField()
    note = models.TextField()
    inventory_check = models.ForeignKey('inventory.InventoryCheck', on_delete=models.SET_NULL, null=True)

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
    date = models.DateField()
    expected_completion_date = models.DateField()
    issuing_inventory_controller = models.ForeignKey('employees.Employee',
        related_name='issuing_inventory_controller', 
        on_delete=models.SET_NULL, null=True,
        limit_choices_to=Q(user__isnull=False))
    receiving_inventory_controller = models.ForeignKey('employees.Employee', 
        on_delete=models.SET_NULL, null=True, 
        limit_choices_to=Q(user__isnull=False))
    actual_completion_date =models.DateField(null=True)#provided later
    source_warehouse = models.ForeignKey('inventory.WareHouse',
        related_name='source_warehouse', on_delete=models.SET_NULL, null=True,)
    receiving_warehouse = models.ForeignKey('inventory.WareHouse', 
        on_delete=models.SET_NULL, null=True,)
    order_issuing_notes = models.TextField(blank=True)
    receive_notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    
    def complete(self):
        '''move all the outstanding items at the same time.'''
        for line in self.transferorderline_set.filter(moved=False):
            line.move()
        self.completed = True
        self.save()

class TransferOrderLine(models.Model):
    # TODO
    # add support later for consumables and equipment
    product = models.ForeignKey('inventory.Product', on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField()
    transfer_order = models.ForeignKey('inventory.TransferOrder', on_delete=models.SET_NULL, null=True)
    moved = models.BooleanField(default=False)

    def move(self):
        '''performs the actual transfer of the item between warehouses'''
        self.transfer_order.source_warehouse.decrement_item(
            self.product, self.quantity)
        self.transfer_order.receiving_warehouse.add_item(
            self.product, self.quantity)
        self.moved=True
        self.save()

class InventoryScrappingRecord(models.Model):
    date = models.DateField()
    controller = models.ForeignKey('employees.Employee', 
        on_delete=models.SET_NULL, null=True,
        limit_choices_to=Q(user__isnull=False))
    warehouse = models.ForeignKey('inventory.WareHouse', on_delete=models.SET_NULL, null=True)
    comments = models.TextField(blank=True)

    @property
    def scrapping_value(self):
        return reduce(lambda x, y: x + y, 
            [i.scrapped_value \
                for i in self.inventoryscrappingrecordline_set.all()], 
                0)

    @property
    def scrapped_items(self):
        return self.inventoryscrappingrecordline_set.all()

    def scrap(self):
        #must be called after all the lines are created
        for item in self.scrapped_items:
            self.warehouse.decrement_item(item.product, item.quantity)




class InventoryScrappingRecordLine(models.Model):
    #add support for equipment and consumables
    product = models.ForeignKey('inventory.Product', on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField()
    note = models.TextField(blank=True)
    scrapping_record = models.ForeignKey('inventory.InventoryScrappingRecord', on_delete=models.SET_NULL, null=True)

    @property
    def scrapped_value(self):
        return self.product.unit_sales_price * D(self.quantity)

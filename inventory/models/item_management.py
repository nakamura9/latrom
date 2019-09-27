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

class OrderPayment(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=16,decimal_places=2)
    order = models.ForeignKey('inventory.order', on_delete=models.SET_NULL, 
        null=True)
    comments = models.TextField()
    entry = models.ForeignKey('accounting.JournalEntry', 
        on_delete=models.SET_NULL,
        blank=True, null=True)

    def create_entry(self, comments=""):
        if self.entry:
            return
        j = JournalEntry.objects.create(
                memo= 'Auto generated journal entry from order payment.' \
                    if comments == "" else comments,
                date=self.date,
                journal =Journal.objects.get(pk=4),
                created_by = self.order.issuing_inventory_controller.employee.user,
                draft=False
            )
        
        j.simple_entry(
            self.amount,
            Account.objects.get(pk=1000),#cash in checking account
            self.order.supplier.account,
        )

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
    
    '''
    order = models.ForeignKey('inventory.Order', on_delete=models.SET_NULL, 
        null=True)
    received_by = models.ForeignKey('inventory.InventoryController', 
        on_delete=models.SET_NULL, 
        null=True,
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

class StockReceiptLine(models.Model):
    receipt = models.ForeignKey('inventory.StockReceipt'
        ,on_delete=models.CASCADE)
    line = models.ForeignKey('inventory.OrderItem', on_delete=models.CASCADE)
    quantity = models.FloatField(default=0.0)


#might need to rename
class InventoryCheck(models.Model):
    date = models.DateField()
    adjusted_by = models.ForeignKey('inventory.InventoryController', 
        on_delete=models.SET_NULL, 
        null=True )
    warehouse = models.ForeignKey('inventory.WareHouse', 
        on_delete=models.SET_NULL, 
        null=True )
    comments = models.TextField()
    
    @property 
    def adjustments(self):
        return self.stockadjustment_set.all()

    @property
    def value_of_all_adjustments(self):
        return sum(
            [i.adjustment_value for i in self.adjustments])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.warehouse.last_inventory_check_date = self.date

class StockAdjustment(models.Model):
    warehouse_item = models.ForeignKey('inventory.WareHouseItem', 
        on_delete=models.SET_NULL, null=True)
    adjustment = models.FloatField()
    note = models.TextField()
    inventory_check = models.ForeignKey('inventory.InventoryCheck', 
        on_delete=models.SET_NULL, null=True)

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
    issuing_inventory_controller = models.ForeignKey('inventory.InventoryController',
        related_name='issuing_inventory_controller', 
        on_delete=models.SET_NULL, null=True)
    receiving_inventory_controller = models.ForeignKey('inventory.InventoryController', 
        on_delete=models.SET_NULL, null=True)
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
        for line in self.transferorderline_set.filter(moved_quantity=0):
            line.move(line.quantity)
        self.completed = True
        self.save()

    def update_completed_status(self):
        # TODO inefficient
        completed = True
        for line in self.transferorderline_set.all():
            if line.quantity > line.moved_quantity:
                completed = False

        self.completed = completed
        self.save()

class TransferOrderLine(models.Model):
    item = models.ForeignKey('inventory.inventoryitem', 
        on_delete=models.SET_NULL, 
        null=True)
    quantity = models.FloatField()
    transfer_order = models.ForeignKey('inventory.TransferOrder', 
        on_delete=models.SET_NULL, null=True)
    moved_quantity = models.FloatField(default=0.0)

    def move(self, quantity, location=None):
        '''performs the actual transfer of the item between warehouses'''
        self.transfer_order.source_warehouse.decrement_item(
            self.item, quantity)
        self.transfer_order.receiving_warehouse.add_item(
            self.item, quantity, location=location)
        self.moved=quantity
        self.save()
        self.transfer_order.update_completed_status()

class InventoryScrappingRecord(models.Model):
    date = models.DateField()
    controller = models.ForeignKey('inventory.InventoryController', 
        on_delete=models.SET_NULL, null=True)
    warehouse = models.ForeignKey('inventory.WareHouse', on_delete=models.SET_NULL, null=True)
    comments = models.TextField(blank=True)

    @property
    def scrapping_value(self):
        return sum(
            [i.scrapped_value \
                for i in self.inventoryscrappingrecordline_set.all()], 
                0)

    @property
    def scrapped_items(self):
        return self.inventoryscrappingrecordline_set.all()

    def scrap(self):
        #must be called after all the lines are created
        for item in self.scrapped_items:
            self.warehouse.decrement_item(item.item, item.quantity)

class InventoryScrappingRecordLine(models.Model):
    item = models.ForeignKey('inventory.inventoryitem', 
        on_delete=models.SET_NULL, 
        null=True)
    quantity = models.FloatField()
    note = models.TextField(blank=True)
    scrapping_record = models.ForeignKey('inventory.InventoryScrappingRecord', on_delete=models.SET_NULL, null=True)

    @property
    def scrapped_value(self):
        #TODO fix 
        if self.item.product_component:
            return self.item.product_component.unit_sales_price * \
                D(self.quantity)

        return 0
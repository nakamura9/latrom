# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from decimal import Decimal as D
import rest_framework
from functools import reduce

from django.db import models
from django.db.models import Q
from django.conf import settings
from accounting.models import JournalEntry, Journal, Account
from common_data.models import SingletonModel
from .item_models import Product, Equipment, Consumable



class WareHouse(models.Model):
    name = models.CharField(max_length=128)
    address = models.TextField()
    description = models.TextField(blank=True)
    inventory_controller = models.ForeignKey('employees.Employee', null=True, 
        blank=True)
    length = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)

    
    @property
    def item_count(self):
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


    def get_item(self, item):
        '''can accept product consumable or equipment as an arg'''
        try:
            if isinstance(item, Product):
                return WareHouseItem.objects.get(product=item, warehouse=self)
            elif isinstance(item, Consumable):
                return WareHouseItem.objects.get(consumable=item, warehouse=self)
            elif isinstance(item, Equipment):
                return WareHouseItem.objects.get(equipment=item, warehouse=self)
            else:
                return None # next code is dead for now
        except:
            return None
            raise NotImplementedError('the selected product does not exist')
    
    def has_item(self, item):
        found_item = self.get_item(item)
        if found_item:
            return(
                found_item.quantity > 0
            )
        return False 
            
    
    def add_item(self, item, quantity):
        #check if record of item is already in warehouse
        if self.has_item(item):
            self.get_item(item).increment(quantity)
            return self.get_item(item)
        else:
            if isinstance(item, Product):
                return self.warehouseitem_set.create(product=item, 
                    quantity=quantity, item_type=1)
            elif isinstance(item, Consumable):
                return self.warehouseitem_set.create(consumable=item, 
                    quantity=quantity, item_type=2)
            elif isinstance(item, Equipment):
                return self.warehouseitem_set.create(equipment=item, 
                    quantity=quantity, item_type=3)
            

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
    ITEM_TYPE_CHOICES = [
        (1, 'Product'),
        (2, 'Consumable'),
        (3, 'Equipment')
    ]
    
    item_type = models.PositiveSmallIntegerField()
    product = models.ForeignKey('inventory.Product',null=True)
    consumable = models.ForeignKey('inventory.Consumable',null=True)
    equipment = models.ForeignKey('inventory.Equipment',null=True)
    quantity = models.FloatField()
    warehouse = models.ForeignKey('inventory.Warehouse', default=1)
    location = models.ForeignKey('inventory.StorageMedia', blank=True, 
        null=True)
    verified = models.BooleanField(default=False)
    #verification expires after the next inventory check date

    def __init__(self, *args, **kwargs):
        super(WareHouseItem, self).__init__(*args, **kwargs)
        self.mapping = {
            1: self.product,
            2: self.consumable, 
            3: self.equipment
        }

    def increment(self, amt):
        amount = float(amt)
        #fix
        
        #if self.quantity + amount > self.product.maximum_stock_level:
        #    raise Exception('Stock level will exceed maximum allowed')
        self.quantity += amount
        self.save()
        return self.quantity

    def decrement(self, amt):
        amount = float(amt)
        #fix
        #if self.quantity < amount:
        #    raise ValueError('Cannot have a quantity less than zero')
        self.quantity -= amount
        self.save()
        # check if min stock level is exceeded
        return self.quantity

    @property
    def name(self):
        #for the api
        return self.item.name

    @property
    def item(self):
        return self.mapping[self.item_type]

class StorageMedia(models.Model):
    name = models.CharField(max_length = 255)
    warehouse = models.ForeignKey('inventory.WareHouse')
    location = models.ForeignKey('inventory.StorageMedia', null=True, blank=True)
    description = models.TextField(blank=True)
    unit = models.ForeignKey('inventory.UnitOfMeasure', null=True, blank=True)
    length = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    capacity = models.FloatField(default=0.0)

    @property
    def children(self):
        return StorageMedia.objects.filter(location=self)

    @property
    def contents(self):
        return WareHouseItem.objects.filter(location=self)
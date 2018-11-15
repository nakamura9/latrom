# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal as D
from functools import reduce

from django.conf import settings
from django.db import models
from django.db.models import Q

from accounting.models import Account, Journal, JournalEntry
from common_data.models import SingletonModel

from .item_models import Consumable, Equipment, Product


class WareHouse(models.Model):
    name = models.CharField(max_length=128)
    address = models.TextField()
    description = models.TextField(blank=True)
    inventory_controller = models.ForeignKey('employees.Employee', 
        on_delete=None, null=True, 
        blank=True,
        limit_choices_to=Q(user__isnull=False))
    length = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)

    
    @property
    def item_count(self):
        '''returns the number of distinct item types in the warehouse'''
        return self.all_items.count()
    
    @property
    def total_item_quantity(self):
        '''returns the total number of physical entities stored in the warehouse'''
        return reduce(lambda x, y: x + y, 
            [i.quantity for i in self.all_items], 0)

    @property
    def all_items(self):
        return self.warehouseitem_set.all()

    def decrement_item(self, item, quantity):
        '''Takes an item and decrements it from the appropriate warehouse item'''
        #safety checks handled elsewhere
        #created to avoid circular imports in invoices
        self.get_item(item).decrement(quantity)


    def get_item(self, item):
        '''can accept product consumable or equipment as an arg'''
        try:
            if isinstance(item, Product):
                return WareHouseItem.objects.get(product=item, warehouse=self)
            elif isinstance(item, Consumable):
                return WareHouseItem.objects.get(consumable=item, 
                    warehouse=self)
            elif isinstance(item, Equipment):
                return WareHouseItem.objects.get(equipment=item, warehouse=self)
            else:
                return None # next code is dead for now
        except:
            return None
            raise ValueError('the selected inventory item does not exist')
    
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
            
        return self.get_item(item)

    def transfer(self, other, item, quantity):
        #transfer stock from current warehouse to other warehouse
        
        if not other.has_item(item):
            other.add_item(item, 0)
        elif not self.has_item(item):
            raise Exception('The source warehouse does not stock this item')

        else:
            source_item = self.get_item(item)
            if quantity > source_item.quantity:
                raise Exception('The transferred quantity is greater than the inventory in stock')
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
    product = models.ForeignKey('inventory.Product', on_delete=None, null=True)
    consumable = models.ForeignKey('inventory.Consumable', on_delete=None, 
        null=True)
    equipment = models.ForeignKey('inventory.Equipment', on_delete=None, 
        null=True)
    quantity = models.FloatField()
    warehouse = models.ForeignKey('inventory.Warehouse', on_delete=None, 
        default=1)
    #might support multiple locations for the same item in the same warehouse
    location = models.ForeignKey('inventory.StorageMedia', blank=True, 
        on_delete=None, null=True)
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

    def __str__(self):
        return self.name

    @property
    def item(self):
        return self.mapping[self.item_type]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.location is None:
            if self.warehouse.storagemedia_set.all().count() == 0:
                # create a default storage medium for each warehouse
                location = StorageMedia.objects.create(
                    name="Default Storage Medium",
                    warehouse=self.warehouse
                )
            else:
                location = self.warehouse.storagemedia_set.first()
            
            self.location = location
            self.save()

class StorageMedia(models.Model):
    name = models.CharField(max_length = 255)
    warehouse = models.ForeignKey('inventory.WareHouse', on_delete=None, )
    location = models.ForeignKey('inventory.StorageMedia', on_delete=None,  
        null=True, blank=True)
    description = models.TextField(blank=True)
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=None,  
        null=True, blank=True)
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

    def __str__(self):
        return self.name
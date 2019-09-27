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
from django.shortcuts import reverse

class WarehouseExeption(Exception):
    pass

class WareHouse(models.Model):
    name = models.CharField(max_length=128)
    address = models.TextField()
    description = models.TextField(blank=True)
    inventory_controller = models.ForeignKey('inventory.InventoryController', 
        on_delete=models.SET_NULL, null=True, 
        blank=True)
    length = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    last_inventory_check_date = models.DateField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("inventory:warehouse-detail", kwargs={"pk": self.pk})
    

    
    @property
    def item_count(self):
        '''returns the number of distinct item types in the warehouse'''
        return self.all_items.count()
    
    @property
    def total_item_quantity(self):
        '''returns the total number of physical entities stored in the warehouse'''
        return sum(
            [i.quantity for i in self.all_items])

    @property
    def all_items(self):
        return self.warehouseitem_set.all()

    def decrement_item(self, item, quantity):
        '''Takes an item and decrements it from the appropriate warehouse item'''
        #safety checks handled elsewhere
        retrieved_item = self.get_item(item)
        if retrieved_item:
            retrieved_item.decrement(quantity)


    def get_item(self, item):
        '''can accept product consumable or equipment as an arg'''
        if WareHouseItem.objects.filter(
            item=item, warehouse=self).exists():
                    
            return WareHouseItem.objects.get(item=item, warehouse=self)
        
        return None # next code is dead for now
        
    def has_item(self, item):
        return self.get_item(item) is not None

    def has_quantity_greater_than_zero(self, item):
        queried_item = self.has_item(item)
        
        if not queried_item: return False

        return queried_item.quantity > 0
    
    def add_item(self, item, quantity, location=None):
        #check if record of item is already in warehouse
        #ignore location if present
        if self.has_item(item) and not location:
            self.get_item(item).increment(quantity)
            
        elif location: 
            location = StorageMedia.objects.get(pk=location)
            print('warehouse location: ', location)
            qs = self.warehouseitem_set.filter(item=item, 
                location=location)
            
            if qs.exists():
                wi = qs.first()
                wi.increment(quantity)
                print('qs: Exists!')
            else:
                print('New Item')
                print('location: ', location)
                print('quantity: ', quantity)
                print('warehouse: ', self)

                WareHouseItem.objects.create(
                    item=item, 
                    location=location, 
                    quantity=quantity,
                    warehouse=self)

        else:
            self.warehouseitem_set.create(item=item, 
                    quantity=quantity, location=location)
            
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
    # NB for now the software will require all items of the same type to be 
    # stored in the same location for the same warehouse.
    
    item = models.ForeignKey('inventory.inventoryitem',
        null=True,
        on_delete=models.SET_NULL)
    quantity = models.FloatField()
    warehouse = models.ForeignKey('inventory.Warehouse', 
        on_delete=models.SET_NULL, null=True, default=1)
    #might support multiple locations for the same item in the same warehouse
    location = models.ForeignKey('inventory.StorageMedia', blank=True, 
        on_delete=models.SET_NULL, null=True)
    verified = models.BooleanField(default=False)
    #verification expires after the next inventory check date


    def increment(self, amt):
        amount = float(amt)
        
        self.quantity += amount
        self.save()
        return self.quantity

    def decrement(self, amt):
        amount = float(amt)
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
    def stock_value(self):
        # TODO test ensure items have stock value implemented
        return D(self.quantity) * self.item.stock_value


    def save(self, *args, **kwargs):
        if self.warehouse.has_item(self.item) and self.pk is None:
            self.warehouse.add_item(self.item, self.quantity)
            return # do not allow a new item to be created
            
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
    warehouse = models.ForeignKey('inventory.WareHouse', on_delete=models.SET_NULL, null=True, )
    location = models.ForeignKey('inventory.StorageMedia', on_delete=models.SET_NULL,
        null=True, blank=True)
    description = models.TextField(blank=True)
    unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=models.SET_NULL,  
        null=True, blank=True)
    length = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    capacity = models.FloatField(default=0.0)

    def get_absolute_url(self):
        return reverse("inventory:storage-media-detail", kwargs={"pk": self.pk})
    

    @property
    def children(self):
        return StorageMedia.objects.filter(location=self)

    @property
    def contents(self):
        return WareHouseItem.objects.filter(location=self)

    def __str__(self):
        return self.name
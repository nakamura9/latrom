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
import invoicing
from accounting.models import Account, Journal, JournalEntry
from common_data.models import SingletonModel, SoftDeletionModel
from django.shortcuts import reverse


class InventoryItem(SoftDeletionModel):
    INVENTORY_TYPES = [
        (0, 'Product'),
        (1, 'Equipment'),
        (2, 'Consumables'),
        (3, 'Raw Material'),]

    name = models.CharField(max_length = 64)
    type = models.PositiveSmallIntegerField(choices=INVENTORY_TYPES)
    category = models.ForeignKey('inventory.Category', 
        on_delete=models.SET_NULL, null=True,default=1)
    length = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    image = models.FileField(blank=True, null=True)
    description = models.TextField(blank=True, default="")
    unit = models.ForeignKey('inventory.UnitOfMeasure', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True, 
        default=1)
    unit_purchase_price = models.DecimalField(max_digits=16, 
        decimal_places=2, 
        default=0.0)
    supplier = models.ForeignKey("inventory.Supplier", 
        on_delete=models.SET_NULL,
        blank=True, 
        null=True)
    minimum_order_level = models.IntegerField( default=0)
    maximum_stock_level = models.IntegerField(default=0)
    #components
    equipment_component = models.OneToOneField('inventory.EquipmentComponent', 
        on_delete=models.SET_NULL,
        null=True)
    product_component = models.OneToOneField('inventory.ProductComponent',
        on_delete=models.SET_NULL,
        null=True)


    def save(self, *args, **kwargs):
        #Strange bug where active is defaulting to false
        if self.pk is None:
            self.active =True
        
        return super().save(*args, **kwargs)

    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if self.equipment_component and hasattr(self.equipment_component, 
                    name):
                return getattr(self.equipment_component, name)
            elif self.product_component and hasattr(self.product_component, 
                    name):
                return getattr(self.product_component, name)


        raise AttributeError(f'{type(self)} has no attribute {name}')

    def get_absolute_url(self):
        if self.type == 0:
            return reverse("inventory:product-detail", kwargs={"pk": self.pk})
        elif self.type == 1:
            return reverse("inventory:equipment-detail", kwargs={"pk": self.pk})
        else:
            return reverse("inventory:consumable-detail", kwargs={"pk": self.pk})
            
    @property
    def consumable_value(self):
        if self.type != 2:
            return D(0)

        current_quantity = self.quantity
        if current_quantity == 0:
            return D(0)

        cummulative_quantity = 0
        orders_with_items_in_stock = []
        partial_orders = False

        #getting the latest orderitems in order of date ordered
        order_items = inventory.models.OrderItem.objects.filter(
            Q(item=self) & 
            Q(
                Q(order__status="order") | 
                Q(order__status="received-partially") |
                Q(order__status="received")
            )).order_by("order__date").reverse()

        #iterate over items
        for item in order_items:
            # orders for which cumulative ordered quantities are less than
            # inventory in hand are considered
            if (item.quantity + cummulative_quantity) < current_quantity:
                orders_with_items_in_stock.append(item)
                cummulative_quantity += item.quantity
                

            else:
                if cummulative_quantity < current_quantity:
                    partial_orders = True
                    orders_with_items_in_stock.append(item)

                else:
                    break


        cumulative_value = D(0)
        if not partial_orders:
            for item in orders_with_items_in_stock:
                cumulative_value += D(item.quantity) * item.order_price

        else:
            for item in orders_with_items_in_stock[:-1]:#remove last elemnt
                cumulative_value += D(item.quantity) * item.order_price

            remainder = current_quantity - cummulative_quantity
            cumulative_value += D(remainder) * \
                orders_with_items_in_stock[-1].order_price
        
        return cumulative_value

    @property
    def consumable_unit_value(self):
        if self.consumable_value > 0:
            return self.consumable_value / D(self.quantity)

        return D(0)

    def __str__(self):
        return str(self.id) + " - " + self.name

    def set_purchase_price(self, price):
        self.unit_purchase_price = price
        self.save()

    @property
    def quantity(self):
        #returns quantity from all warehouses
        items = inventory.models.WareHouseItem.objects.filter(item=self)
        return sum([i.quantity for i in items])

    @property
    def locations(self):
        return inventory.models.WareHouseItem.objects.filter(
            Q(item=self),
            Q(quantity__gt=0)
            )

    @property
    def unit_sales_price(self):
        if self.product_component:
            return self.product_component.unit_sales_price

        return D(0)

    @staticmethod
    def total_inventory_value():
        return sum([p.product_component.stock_value for p in InventoryItem.objects.filter(product_component__isnull=False)])


class ProductComponent(models.Model):
    PRICING_CHOICES = [
    (0, 'Manual'),
    (1, 'Margin'),
    (2, 'Markup')
]
    pricing_method = models.IntegerField(choices=PRICING_CHOICES, default=0)
    direct_price = models.DecimalField(max_digits=16, decimal_places=2)
    margin = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    markup = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    sku = models.CharField(max_length=16, blank=True)
    tax = models.ForeignKey('accounting.tax', 
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL)
    


    def quantity_on_date(self, date):
        '''
        Starts with current quantity
        going back subtract the received invetory
        add the sold inventory
        return the result
        i.e.
            on_date = current - orders( + debit notes ) + sold(- credit notes) + scrapped inventory
        '''
        current_quantity = self.inventoryitem.quantity
        print('Current: ', current_quantity)
        total_orders = inventory.models.order.OrderItem.objects.filter(
            Q(order__date__gte=date) &
            Q(order__date__lte=datetime.date.today()) &
            Q(item=self.inventoryitem)
        ).exclude(order__status="draft")

        ordered_quantity = sum([i.received - i.returned_quantity \
                for i in total_orders])

        # will eventually replace with dispatch data
        total_sales = invoicing.models.InvoiceLine.objects.filter(
            Q(invoice__date__gte=date) &
            Q(invoice__date__lte=datetime.date.today()) &
            Q(product__product=self.inventoryitem) &
            Q(invoice__draft=False) &
            Q(
                Q(invoice__status="paid") |
                Q(invoice__status="invoice") |
                Q(invoice__status="paid-partially")
            )
        )

        sold_quantity = sum(
            [(i.product.quantity - D(i.product.returned_quantity)) \
                for i in total_sales])


        return D(current_quantity) + sold_quantity - D(ordered_quantity)
    
    @property
    def parent(self):
        return InventoryItem.objects.get(product_component=self)

    @property
    def unit_sales_price(self):
        if self.pricing_method == 0:
            return self.direct_price
        elif self.pricing_method == 1:
            return D(self.parent.unit_purchase_price / D(1 - self.margin))
        else:
            return D(self.parent.unit_purchase_price * D(1 + self.markup))


    @property 
    def unit_value(self):
        '''the value of inventory on a per item basis'''
        if self.inventoryitem.quantity  == 0 or self.stock_value == 0:
            return self.inventoryitem.unit_purchase_price
        return self.stock_value / D(self.inventoryitem.quantity)

    @property
    def stock_value(self):
        '''.
        averaging- calculating the overall stock value on the average of all
        the values for the quantity in stock.
        '''  
        current_quantity = self.parent.quantity
        cummulative_quantity = 0
        orders_with_items_in_stock = []
        partial_orders = False

        if current_quantity == 0:
            return 0

        #getting the latest orderitems in order of date ordered
        order_items = inventory.models.OrderItem.objects.filter(
            Q(item=self.parent) & 
            Q(
                Q(order__status="order") | 
                Q(order__status="received-partially") |
                Q(order__status="received")
            )).order_by("order__date").reverse()

        #iterate over items
        for item in order_items:
            # orders for which cumulative ordered quantities are less than
            # inventory in hand are considered
            if (item.quantity + cummulative_quantity) < current_quantity:
                orders_with_items_in_stock.append(item)
                cummulative_quantity += item.quantity
                

            else:
                if cummulative_quantity < current_quantity:
                    partial_orders = True
                    orders_with_items_in_stock.append(item)

                else:
                    break


        cumulative_value = D(0)
        if not partial_orders:
            for item in orders_with_items_in_stock:
                cumulative_value += D(item.quantity) * item.order_price

        else:
            for item in orders_with_items_in_stock[:-1]:
                cumulative_value += D(item.quantity) * item.order_price

            remainder = current_quantity - cummulative_quantity
            cumulative_value += D(remainder) * \
                orders_with_items_in_stock[-1].order_price
        
        return cumulative_value


    @property
    def sales_to_date(self):
        items = invoicing.models.ProductLineComponent.objects.filter(
            product=self.inventoryitem)
        total_sales = sum(
            [(item.invoiceline.subtotal - item.invoiceline.tax_) for item in items])
        return total_sales
    

class EquipmentComponent(models.Model):
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('poor', 'Poor'),
        ('broken', 'Not Functioning')
    ]
    condition = models.CharField(max_length=16, 
        choices=CONDITION_CHOICES, default='excellent')
    asset_data = models.ForeignKey('accounting.Asset', 
        on_delete=models.SET_NULL,
        null=True, blank=True)
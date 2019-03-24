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
    image = models.FileField(blank=True, null=True, 
        upload_to=settings.MEDIA_ROOT)
    description = models.TextField(blank=True, default="")
    unit = models.ForeignKey('inventory.UnitOfMeasure', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True, 
        default=1)
    unit_purchase_price = models.DecimalField(max_digits=9, 
        decimal_places=2, 
        default=0.0)
    supplier = models.ForeignKey("inventory.Supplier", 
        on_delete=models.SET_NULL,
        blank=True, 
        null=True)
    minimum_order_level = models.IntegerField( default=0)
    maximum_stock_level = models.IntegerField(default=0)
    #components
    equipment_component = models.ForeignKey('inventory.EquipmentComponent', 
        on_delete=models.SET_NULL,
        null=True)
    product_component = models.ForeignKey('inventory.ProductComponent',
        on_delete=models.SET_NULL,
        null=True)


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


class ProductComponent(models.Model):
    PRICING_CHOICES = [
    (0, 'Manual'),
    (1, 'Margin'),
    (2, 'Markup')
]
    pricing_method = models.IntegerField(choices=PRICING_CHOICES, default=0)
    direct_price = models.DecimalField(max_digits=9, decimal_places=2)
    margin = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    markup = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    sku = models.CharField(max_length=16, blank=True)

    @staticmethod
    def total_inventory_value():
        return sum([p.stock_value for p in InventoryItem.objects.filter(type=0)])


    def quantity_on_date(self, date):
        current_quantity = self.quantity

        total_orders = inventory.models.order.OrderItem.objects.filter(
            Q(order__date__gte=date) &
            Q(order__date__lte=datetime.date.today()) &
            Q(item=self)
        )

        ordered_quantity = sum([i.received for i in total_orders])

        total_sales = invoicing.models.SalesInvoiceLine.objects.filter(
            Q(invoice__date__gte=date) &
            Q(invoice__date__lte=datetime.date.today()) &
            Q(item=self)
        )

        sold_quantity = sum([(i.quantity - i.returned_quantity) \
                for i in total_sales])

        return current_quantity + sold_quantity - ordered_quantity

    @staticmethod
    def total_inventory_quantity_on_date(date):
        # TODO test
        '''Takes a date and returns the inventory quantity on that date
        takes todays inventory 
        starting = todays + sold - ordered'''
        current_total_product_quantity = sum([i.quantity \
                for i in InventoryItem.objects.all()])

        total_product_orders = inventory.models.order.OrderItem.objects.filter(
            Q(order__date__gte=date) &
            Q(order__date__lte=datetime.date.today()) &
            Q(item_type=1)
        )

        ordered_quantity = sum([i.received for i in total_product_orders])

        total_product_sales = invoicing.models.SalesInvoiceLine.objects.filter(
            Q(invoice__date__gte=date) &
            Q(invoice__date__lte=datetime.date.today())
        )

        sold_quantity = sum([(i.quantity - i.returned_quantity) \
                for i in total_product_sales])

        return current_total_product_quantity + sold_quantity - ordered_quantity
    
    @property
    def parent(self):
        return InventoryItem.objects.get(product_component=self)

    @property
    def unit_sales_price(self):
        if self.pricing_method == 0:
            return self.direct_price
        elif self.pricing_method == 1:
            return D(self.parent.unit_purchase_price / (1 - self.margin))
        else:
            return D(self.parent.unit_purchase_price * (1 + self.markup))


    @property 
    def unit_value(self):
        '''the value of inventory on a per item basis'''
        if self.quantity  == 0:
            return 0
        return self.stock_value / D(self.quantity)

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
            item=self.parent).order_by("order__date").reverse()

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
        items = invoicing.models.SalesInvoiceLine.objects.filter(
            product=self)
        total_sales = sum(
            [D(item.quantity) * item.price for item in items])
        return total_sales
    

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
        items= [Event(inv.invoice.date, 
            'sold %d items as part of sales invoice %d ' % (
                inv.quantity, inv.invoice.pk)) \
                    for inv in invoicing.models.SalesInvoiceLine.objects.filter(
                        Q(product=self) & Q(invoice__date__gte=epoch))]
        # from orders
        orders = [Event(o.order.date, 
            "added %d items to inventory from purchase order #%d." % (o.received, o.order.pk)) \
                for o in inventory.models.OrderItem.objects.filter(Q(product=self) 
                    & Q(order__date__gte= epoch)) if o.received > 0]

        events = items + orders 
        return sorted(events)

    

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
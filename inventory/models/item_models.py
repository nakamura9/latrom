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
import inventory
import invoicing

class BaseItem(models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length = 64)
    category = models.ForeignKey('inventory.Category', default=1)
    active = models.BooleanField(default=True)
    length = models.FloatField(default=0.0)
    width = models.FloatField(default=0.0)
    height = models.FloatField(default=0.0)
    image = models.FileField(blank=True, null=True, 
        upload_to=settings.MEDIA_ROOT)
    description = models.TextField(blank=True, default="")
    unit = models.ForeignKey('inventory.UnitOfMeasure', blank=True, default=1)
    unit_purchase_price = models.DecimalField(max_digits=6, decimal_places=2)
    supplier = models.ForeignKey("inventory.Supplier", blank=True, null=True)
    def __str__(self):
        return str(self.id) + " - " + self.name

    def set_purchase_price(self, price):
        self.unit_purchase_price = price
        self.save()

    @property
    def quantity(self):
        #returns quantity from all warehouses
        if isinstance(self, Product):
            items = inventory.models.WareHouseItem.objects.filter(product=self)
        if isinstance(self, Consumable):
            items = inventory.models.WareHouseItem.objects.filter(consumable=self)
        if isinstance(self, Equipment):
            items = inventory.models.WareHouseItem.objects.filter(equipment=self)
        return reduce(lambda x, y: x + y, [i.quantity for i in items], 0)

    @property
    def stock_value(self):
        raise NotImplementedError()

class Product(BaseItem):
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
    pricing_method = models.IntegerField(choices=PRICING_CHOICES, default=0)
    direct_price = models.DecimalField(max_digits=9, decimal_places=2)
    margin = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    markup = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    sku = models.CharField(max_length=16, blank=True)
    minimum_order_level = models.IntegerField(default=0)
    maximum_stock_level = models.IntegerField(default=0)

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

        
    @property
    def sales_to_date(self):
        return 0 #!!fix
        items = invoicing.models.SalesInvoiceLine.objects.filter(product=self)
        total_sales = reduce(lambda x,y: x + y, [product.quantity * product.price for item in items], 0)
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
        # from orders
        orders = [Event(o.order.issue_date, 
            "added %d items to inventory from purchase order #%d." % (o.received, o.order.pk)) \
                for o in inventory.models.OrderItem.objects.filter(Q(product=self) 
                    & Q(order__issue_date__gte= epoch)) if o.received > 0]

        events = items + orders 
        return sorted(events)

class RawMaterial(BaseItem):
    minimum_order_level = models.IntegerField( default=0)
    maximum_stock_level = models.IntegerField(default=0)

class Equipment(BaseItem):
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('poor', 'Poor'),
        ('broken', 'Not Functioning')
    ]
    condition = models.CharField(max_length=16, 
        choices=CONDITION_CHOICES, default='excellent')
    asset_data = models.ForeignKey('accounting.Asset', null=True, blank=True)

class Consumable(BaseItem):
    minimum_order_level = models.IntegerField( default=0)
    maximum_stock_level = models.IntegerField(default=0)

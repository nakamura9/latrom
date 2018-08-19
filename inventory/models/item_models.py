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
from warehouse_models import WareHouseItem
from item_management import OrderItem

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
    supplier = models.ForeignKey("inventory.Supplier", blank=True, null=True)
    def __str__(self):
        return str(self.id) + " - " + self.name

    @property
    def quantity(self):
        #returns quantity from all warehouses
        items = WareHouseItem.objects.filter(product=self)
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
    unit_purchase_price = models.DecimalField(max_digits=6, decimal_places=2)
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

        #dates under consideration 
        TODAY  = datetime.date.today()
        START = TODAY - datetime.timedelta(days=30)
        
        #get the most recent price older than 30 days
        older_items = OrderItem.objects.filter(
            Q(product=self) 
            & Q(received__gt = 0)
            & Q(order__issue_date__lt = START))

        if older_items.count() > 0:
            previous_price = older_items.latest('order__issue_date').order_price
        else:
            #uses the oldest available price. not implemented here
            previous_price = self.unit_purchase_price
         
        # get the ordered items from the last 30 days.
        ordered_in_last_month = OrderItem.objects.filter(
            Q(product=self) 
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
        items = InvoiceItem.objects.filter(product=self)
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
                for o in OrderItem.objects.filter(Q(product=self) 
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

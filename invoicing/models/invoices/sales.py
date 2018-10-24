# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import itertools
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone

import inventory
from accounting.models import Account, Expense, Journal, JournalEntry, Tax
from common_data.models import Person, SingletonModel
from employees.models import Employee
from invoicing.models.payment import Payment
from services.models import Service

from .abstract import AbstractSale


class SalesInvoice(AbstractSale):
    '''used to charge for finished products'''
    DEFAULT_WAREHOUSE = 1 #make fixture
    purchase_order_number = models.CharField(blank=True, max_length=32)
    #add has returns field
    ship_from = models.ForeignKey('inventory.WareHouse', on_delete=None,
         default=DEFAULT_WAREHOUSE)

    def add_product(self, product, quantity):
        self.salesinvoiceline_set.create(
            product=product, 
            quantity=quantity,
            price=product.unit_sales_price,
            invoice=self
        )

    @property
    def returned_total(self):
        return reduce(lambda x,y: x + y, 
            [i.returned_value for i in self.salesinvoiceline_set.all()], 0)

    @property
    def subtotal(self):
        return reduce(lambda x, y: x+ y, 
            [i.subtotal for i in self.salesinvoiceline_set.all()], 0)

    def update_inventory(self):
        #called in views.py
        for line in self.salesinvoiceline_set.all():
            #check if ship_from has the product in sufficient quantity
             self.ship_from.decrement_item(line.product, line.quantity)

    def create_entry(self):
        '''sales entries debits the inventory and in the case of credit 
        sales credits the customer account or the cash book otherwise.
        First a journal entry is made to debit the inventory and credit the 
        customer account. If the invoice is on credit nothing further happens.
        However if it is a cash invoice, the payment object is created along with its accompanying entry.'''
        j = JournalEntry.objects.create(
                reference='INV' + str(self.pk),
                memo= 'Auto generated entry from sales invoice.',
                date=self.date,
                journal =Journal.objects.get(pk=1)#Cash receipts Journal
            )
        j.credit(self.total, Account.objects.get(pk=4009))#inventory
        j.debit(self.subtotal, Account.objects.get(pk=4000))#sales
        if self.tax_amount > D(0):
            j.debit(self.tax_amount, Account.objects.get(pk=2001))#sales tax

            return j
        if not self.on_credit:
            pmt = Payment.objects.create(
                payment_for=0,
                sales_invoice=self,
                amount=self.total,
                date=self.due,
                sales_rep=self.salesperson
            )
            pmt.create_entry()

class SalesInvoiceLine(models.Model):
    invoice = models.ForeignKey('invoicing.SalesInvoice',on_delete=models.CASCADE,)
    product = models.ForeignKey("inventory.Product", on_delete=None)
    quantity = models.FloatField(default=0.0)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    discount = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    returned_quantity = models.FloatField(default=0.0)
    returned = models.BooleanField(default=False)

    @property
    def subtotal(self):
        return D(self.quantity) * self.price

    def _return(self, quantity):
        self.returned_quantity += float(quantity)
        self.returned = True
        self.save()

    @property
    def returned_value(self):
        if self.price == D(0.0):
            return self.product.unit_sales_price * D(self.returned_quantity)
        return self.price * D(self.returned_quantity)

    def save(self, *args, **kwargs):
        super(SalesInvoiceLine, self).save(*args, **kwargs)
        if self.returned_quantity > 0:
            self.returned = True
            
        if self.price == 0.0 and self.product.unit_sales_price != D(0.0):
            self.price = self.product.unit_sales_price
            self.save()

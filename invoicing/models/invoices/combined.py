# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone

from common_data.models import Person
from services.models import Service
from accounting.models import Account, Journal, JournalEntry, Tax, Expense
from employees.models import Employee
from common_data.models import SingletonModel
import inventory
import itertools
from .abstract import AbstractSale

class CombinedInvoice(AbstractSale):
    '''Basic Invoice format with description and amount fields 
    that combines the features of sales, services and bills'''
    
    def add_line(self, data):
        if data['lineType'] == 'sale':
            pk = data['data']['item'].split('-')[0]
            product = inventory.models.Product.objects.get(pk=pk)
            self.combinedinvoiceline_set.create(
                line_type=1,#product
                quantity_or_hours= data['data']['quantity'],
                product=product
            )
        
        elif data['lineType'] == 'service':
            pk, name = data['data']['service'].split('-')
            service = Service.objects.get(pk=pk)
            self.combinedinvoiceline_set.create(
                line_type=2,#service
                quantity_or_hours= data['data']['hours'],
                service=service
            )

        elif data['lineType'] == 'billable':
            pk, name = data['data']['billable'].split('-')
            expense = Expense.objects.get(pk=pk)
            self.combinedinvoiceline_set.create(
                line_type=3,#expense
                expense=expense
            )

    @property
    def subtotal(self):
        return reduce(lambda x, y: x + y,
            [i.subtotal for i in self.combinedinvoiceline_set.all()], 0)

class CombinedInvoiceLine(models.Model):
    LINE_CHOICES = [
        (1, 'product'),
        (2, 'service'),
        (3, 'expense'),
    ]
    invoice = models.ForeignKey('invoicing.CombinedInvoice', on_delete=None, default=1)
    expense = models.ForeignKey('accounting.Expense',on_delete=None, null=True)
    service = models.ForeignKey('services.Service',on_delete=None, null=True)
    product = models.ForeignKey("inventory.Product", on_delete=None,null=True)
    line_type = models.PositiveSmallIntegerField(choices=LINE_CHOICES)
    quantity_or_hours = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)

    def __str__(self):
        if self.line_type == 1:
            return '[ITEM] {} x {} @ ${}{}'.format(
                self.quantity_or_hours,
                str(self.product).split('-')[1],
                self.product.unit_sales_price,
                self.product.unit
            )
        elif self.line_type == 2:
            return '[SERVICE] {} Flat fee: ${} + {}Hrs @ ${}/Hr'.format(
                self.service.name,
                self.service.flat_fee,
                self.quantity_or_hours,
                self.service.hourly_rate
            )
        elif self.line_type ==3:
            return '[BILLABE EXPENSE] %s' % self.expense.description

    @property
    def subtotal(self):
        if self.line_type == 1:
            return self.product.unit_sales_price * self.quantity_or_hours
        elif self.line_type == 2:
            return self.service.flat_fee + \
                 (self.service.hourly_rate * self.quantity_or_hours)
        elif self.line_type ==3:
            return self.expense.amount

        return 0

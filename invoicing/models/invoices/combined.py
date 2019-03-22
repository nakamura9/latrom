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
from services.models import Service, WorkOrderRequest

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
            pk = data['data']['service'].split('-')[0]
            service = Service.objects.get(pk=pk)
            self.combinedinvoiceline_set.create(
                line_type=2,#service
                quantity_or_hours= data['data']['hours'],
                service=service
            )

            if not self.status in ['quotation', 'draft']:
                if not WorkOrderRequest.objects.filter(
                        combined_invoice=self, service=service).exists():
                    WorkOrderRequest.objects.create(
                        combined_invoice=self, 
                        service=service,
                        invoice_type=1,
                        status="request"
                    )

        elif data['lineType'] == 'billable':
            pk = data['data']['billable'].split('-')[0]
            expense = Expense.objects.get(pk=pk)
            self.combinedinvoiceline_set.create(
                line_type=3,#expense
                expense=expense
            )

    @property
    def subtotal(self):
        return sum(
            [i.subtotal for i in self.combinedinvoiceline_set.all()])

    def create_entry(self):
        j = JournalEntry.objects.create(
                memo= 'Auto generated entry from invoice.',
                date=self.date,
                journal =Journal.objects.get(pk=1),#Cash receipts Journal
                created_by = self.salesperson.employee.user,
                draft=False
            )

        j.credit(self.subtotal, Account.objects.get(pk=4000))

        j.debit(self.total, self.customer.account)

        if self.tax_amount > D(0):
            j.credit(self.tax_amount, Account.objects.get(pk=2001))#sales tax

        self.entry = j
        self.save()
        return j

    def _line_total(self, line_type):
        total = D(0)
        for line in line_type:
            total += line.subtotal

        return total

    def _line_getter(self, type_id):
        return CombinedInvoiceLine.objects.filter(
            Q(invoice=self) & Q(line_type=type_id))
    
    @property
    def sales_lines(self):
        return self._line_getter(1)

    @property 
    def sales_total(self):
        return self._line_total(self.sales_lines)


    @property
    def service_lines(self):
        return self._line_getter(2)

    @property
    def service_total(self):
        return self._line_total(self.service_lines)
        

    @property
    def expense_lines(self):
        return self._line_getter(3)

    @property
    def expense_total(self):
        return self._line_total(self.expense_lines)
        

class CombinedInvoiceLine(models.Model):
    LINE_CHOICES = [
        (1, 'product'),
        (2, 'service'),
        (3, 'expense'),
    ]
    invoice = models.ForeignKey('invoicing.CombinedInvoice', on_delete=models.SET_NULL, null=True, default=1)
    expense = models.ForeignKey('accounting.Expense',on_delete=models.SET_NULL, null=True, )
    service = models.ForeignKey('services.Service',on_delete=models.SET_NULL, null=True,)
    product = models.ForeignKey("inventory.Product", on_delete=models.SET_NULL, null=True,)
    line_type = models.PositiveSmallIntegerField(choices=LINE_CHOICES)
    quantity_or_hours = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)

    def __str__(self):
        if self.line_type == 1:
            return '[ITEM] {} x {} @ ${:0.2f}{}'.format(
                self.quantity_or_hours,
                str(self.product).split('-')[1],
                self.product.unit_sales_price,
                self.product.unit
            )
        elif self.line_type == 2:
            return '[SERVICE] {} Flat fee: ${:0.2f} + {}Hrs @ ${:0.2f}/Hr'.format(
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
            return self.expense.amount if self.expense else 0

        return 0

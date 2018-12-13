# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import itertools
from decimal import Decimal as D
from functools import reduce

from django.db import models
from django.db.models import Q
from django.utils import timezone

from accounting.models import Account, Expense, Journal, JournalEntry, Tax
from invoicing import models as inv_models
from services.models import Service


class AbstractSale(models.Model):
    DEFAULT_TAX = 1
    DEFAULT_SALES_REP = 1
    DEFAULT_CUSTOMER = 1
    SALE_STATUS = [
        ('quotation', 'Quotation'),
        ('draft', 'Draft'),
        ('invoice', 'Invoice'),
        ('paid', 'Paid In Full'),
        ('paid-partially', 'Paid Partially'),
        ('reversed', 'Reversed'),
    ]
    status = models.CharField(max_length=16, choices=SALE_STATUS)
    invoice_number = models.PositiveIntegerField(null=True)
    quotation_number = models.PositiveIntegerField(null=True)
    customer = models.ForeignKey("invoicing.Customer", on_delete=None,default=DEFAULT_CUSTOMER)
    salesperson = models.ForeignKey('invoicing.SalesRepresentative',
        on_delete=None, default=DEFAULT_SALES_REP)
    active = models.BooleanField(default=True)
    due= models.DateField( default=datetime.date.today)
    date= models.DateField(default=datetime.date.today)
    discount = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    tax = models.ForeignKey('accounting.Tax', on_delete=None,blank=True, 
        null=True)
    terms = models.CharField(max_length = 128, blank=True)
    comments = models.TextField(blank=True)
    entry = models.ForeignKey('accounting.JournalEntry', 
        on_delete=None, blank=True, null=True)
    @property
    def overdue(self):
        '''returns boolean'''
        return self.overdue_days < 0

    @property
    def overdue_days(self):
        '''returns days due'''
        TODAY = timezone.now().date()

        if self.due < TODAY:
            return (self.due - TODAY).days
        return 0
        
    @staticmethod
    def abstract_filter(filter):
        '''wrap all filters in one Q object and pass it to this function'''
        sales = inv_models.SalesInvoice.objects.filter(filter)
        service = inv_models.ServiceInvoice.objects.filter(filter)
        bill = inv_models.Bill.objects.filter(filter)
        combined = inv_models.CombinedInvoice.objects.filter(filter)
        invoices = itertools.chain(sales, service, bill, combined)

        return invoices

    def delete(self, *args, **kwargs):
        if self.status == "draft":
            super().delete(*args, **kwargs)
        else:
            self.active = False
            self.save()
    
    @property
    def total(self):
        return self.subtotal + self.tax_amount

    @property
    def is_quotation(self):
        return self.status == 'quotation'

    @property
    def on_credit(self):
        # might need to improve the logic
        return self.status == 'invoice' and \
            self.due < self.date and \
            self.total_due > 0

    @property
    def total_paid(self):
        return reduce(lambda x,y: x + y, 
            [p.amount for p in self.payment_set.all()], 0)

    @property
    def total_due(self):
        return self.total - self.total_paid

    @property
    def tax_amount(self):
        if self.tax and self.tax.rate != 0:
            return self.subtotal * D((self.tax.rate / 100.0)).quantize(D('1.00'))
        return 0

    @property
    def subtotal(self):
        raise NotImplementedError()

    def __str__(self):
        return 'SINV' + str(self.pk)

    def set_quote_invoice_number(self):
        # add feature to allow invoices to be viewed as
        config = inv_models.SalesConfig.objects.first() 
        if self.is_quotation:
            if self.quotation_number is None:
                self.quotation_number = config.next_quotation_number
                config.next_quotation_number += 1
                config.save()
                self.save()
        elif self.status != 'draft':
            if self.invoice_number is None:
                self.invoice_number = config.next_invoice_number
                config.next_invoice_number += 1
                config.save()
                self.save()
        else:
            return

    def save(self, *args, **kwargs):
        super(AbstractSale, self).save(*args, **kwargs)
        config = inv_models.SalesConfig.objects.first()
        if self.tax is None and config.sales_tax is not None:
            self.tax = config.sales_tax
            self.save()
        self.set_quote_invoice_number()

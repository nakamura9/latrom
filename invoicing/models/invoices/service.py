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
from services.models import Service

from .abstract import AbstractSale


class ServiceInvoice(AbstractSale):
    '''Used to charge clients for a service'''

    def add_line(self, service_id, hours):
        service = Service.objects.get(pk=service_id)
        self.serviceinvoiceline_set.create(
            service=service,
            hours=hours)

    @property
    def subtotal(self):
        return reduce(lambda x,y: x + y, 
            [i.total for i in self.serviceinvoiceline_set.all() ], 0)

    def create_entry(self):
        print('[warning] A n entry method needs to be implemented that factors '
        'in all the types of lines in a combined invoice')

class ServiceInvoiceLine(models.Model):
    invoice = models.ForeignKey('invoicing.ServiceInvoice', on_delete=models.CASCADE,)
    service = models.ForeignKey('services.Service', on_delete=None)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    
    @property
    def total(self):
        return self.service.flat_fee + (self.service.hourly_rate * self.hours)

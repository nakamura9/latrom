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


class Bill(AbstractSale):
    '''Used to recover billable expenses'''
    
    customer_reference = models.CharField(max_length=255, blank=True)
    
    @property
    def billable_expenses(self):
        return self.customer.expense_set.filter(Q(billline__isnull=True))

    def add_line(self, expense_id):
        expense = Expense.objects.get(pk=expense_id)
        if expense:
            self.billline_set.create(
                expense=expense
            )
        
    @property
    def subtotal(self):
        return reduce(lambda x, y: x + y, 
            [line.expense.amount for line in self.billline_set.all() if line.expense], 0)
    
    def __str__(self):
        return "Bill - {}".format(self.pk)


    @property
    def total(self):
        # no tax on bills 
        return self.subtotal
    
    def create_entry(self):
        #verified
        j = JournalEntry.objects.create(
            memo= 'Auto generated Entry from unpaid bill from customer.',
            date=self.date,
            journal =Journal.objects.get(pk=3),#Sales Journal
            created_by = self.salesperson.employee.user,
            draft=False
        )
        #check these accounts
        # the corresponding account for the expense incurred
        for line in self.billline_set.all():
            j.credit(line.expense.amount, line.expense.expense_account)
        j.debit(self.total, self.customer.account)#customer account

        self.entry = j
        self.save()

        return j
            
class BillLine(models.Model):
    bill = models.ForeignKey('invoicing.Bill', on_delete=models.SET_NULL, null=True)
    expense = models.ForeignKey('accounting.Expense', on_delete=models.SET_NULL, null=True)

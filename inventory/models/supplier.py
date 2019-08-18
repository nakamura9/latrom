# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal as D

from django.db import models
from django.db.models import Q

from accounting.models import Account
from common_data.models import  SoftDeletionModel
from inventory.models.item import InventoryItem
from inventory.models.item_management import StockReceipt
from inventory.models.order import Order


class Supplier(SoftDeletionModel):
    '''The businesses and individuals that provide the organization with 
    products it will sell. Basic features include contact details address and 
    contact people.
    The account of the supplier is for instances when orders are made on credit.'''
    # one or the other 
    organization = models.OneToOneField('common_data.Organization',
         on_delete=models.SET_NULL, blank=True,
         null=True)
    individual = models.OneToOneField('common_data.Individual', 
        on_delete=models.SET_NULL, blank=True, 
        null=True)
    account = models.ForeignKey('accounting.Account', 
        on_delete=models.SET_NULL, 
        blank=True, null=True)
    banking_details=models.TextField(blank=True, default="")
    billing_address=models.TextField(blank=True, default="")

    @property
    def name(self):
        if self.organization:
            return self.organization.legal_name
        else:
            return self.individual.full_name

    @property
    def phone(self):
        if self.organization:
            return self.organization.phone
        else:
            return self.individual.phone

    @property
    def is_organization(self):
        return self.organization != None

    @property
    def email(self):
        if self.is_organization:
            return self.organization.email
        else:
            return self.individual.email

    @property
    def address(self):
        if self.is_organization:
            return self.organization.business_address
        else:
            return self.individual.address

    @property
    def name(self):
        if self.is_organization:
            return str(self.organization)
        else:
            return str(self.individual)
        
    def __str__(self):
        return self.name

    @property
    def products(self):
        return InventoryItem.objects.filter(type=0, supplier=self)

    @property
    def consumables(self):
        return InventoryItem.objects.filter(type=2, supplier=self)

    @property
    def equipment(self):
        return InventoryItem.objects.filter(type=1, supplier=self)

    @property
    def last_delivery(self):
        qs = StockReceipt.objects.filter(order__supplier=self)
        if qs.exists():
            return qs.latest('pk')
        return None

    @property
    def average_days_to_deliver(self):
        qs = Order.objects.filter(supplier=self)
        total_days = 0
        fully_received = 0
        for order in qs:
            if order.fully_received and order.stockreceipt_set.count() > 0:
                # orders can have multiple stock receipts
                fully_received += 1
                
                last_receipt = order.stockreceipt_set.latest('receive_date')
                total_days += (last_receipt.receive_date - order.date).days
        
        if fully_received > 0:
            print(f'{self} has {fully_received} orders')
            return total_days / fully_received

        return 0

    def create_account(self):
        if self.account is None:
            n_suppliers = Supplier.objects.all().count()
            #will overwrite if error occurs
            self.account = Account.objects.create(
                name= "Vendor: %s" % self.name,
                id = 2100 + n_suppliers + 1, # the + 1 for the default supplier
                balance =0,
                type = 'liability',
                description = 'Account which represents debt owed to a Vendor',
                balance_sheet_category='current-liabilities',
                parent_account= Account.objects.get(pk=2000)# trade payables
            )
    
    def save(self, *args, **kwargs):
        if self.account is None:
            self.create_account()
        super().save(*args, **kwargs)


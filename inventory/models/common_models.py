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
from item_models import Product

class InventorySettings(SingletonModel):
    INVENTORY_VALUATION_METHODS = [
        (1, 'Averaging'),
        (2, 'FIFO'),
        (3, 'LIFO'),
        (4, 'Last order price')
    ]
    PRICING_METHODS = [
        (1, 'Direct Pricing'),
        (2, 'Margin'),
        (3, 'Markup')
    ]
    DOCUMENT_THEME_CHOICES = [
        (1, 'Simple'),
        (2, 'Blue'),
        (3, 'Steel'),
        (4, 'Verdant'),
        (5, 'Warm')
    ]
    INVENTORY_CHECK_FREQUENCY = [
        (1, 'Monthly'),
        (2, 'Quarterly'),
        (3, 'Bi-Annually'),
        (4, 'Annually')
    ]
    INVENTORY_CHECK_DATE = [
        (i, i) for i in range(28, 1)
    ]
    inventory_valuation_method = models.PositiveSmallIntegerField(
        choices = INVENTORY_VALUATION_METHODS, default=1
    )
    product_sales_pricing_method= models.PositiveSmallIntegerField(
        choices=PRICING_METHODS, default=1
    )
    order_template_theme = models.PositiveSmallIntegerField(
        choices=DOCUMENT_THEME_CHOICES, default=1
    )
    inventory_check_frequency = models.PositiveSmallIntegerField(
        choices=INVENTORY_CHECK_FREQUENCY, default=1
    )
    inventory_check_date = models.PositiveSmallIntegerField(
        choices=INVENTORY_CHECK_DATE, default=1
    )
    use_warehousing_model = models.BooleanField(default=True)
    use_storage_media_model = models.BooleanField(default=True)

class InventoryController(models.Model):
    '''Model that represents employees with the role of 
    inventory controller and have the ability to make purchase orders,
    receive them, transfer inventory between warehouses and perform other 
    functions.'''
    employee = models.ForeignKey('employees.Employee')
    can_authorize_equipment_requisitions = models.BooleanField(default=False)
    can_authorize_consumables_requisitions = models.BooleanField(default=False)


class Supplier(models.Model):
    '''The businesses and individuals that provide the organization with 
    products it will sell. Basic features include contact details address and 
    contact people.
    The account of the supplier is for instances when orders are made on credit.'''
    # one or the other 
    organization = models.OneToOneField('common_data.Organization', null=True)
    individual = models.OneToOneField('common_data.Individual', null=True)
    active = models.BooleanField(default=True)
    account = models.ForeignKey('accounting.Account',blank=True, null=True)

    @property
    def name(self):
        if self.organization:
            return self.organization.legal_name
        else:
            return self.individual.full_name

    @property
    def is_organization(self):
        return self.organization != None

    @property
    def supplier_email(self):
        if self.is_organization:
            return self.organization.email
        else:
            return self.individual.email

    @property
    def address(self):
        if self.is_organization:
            return self.organization.address
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

    def save(self, *args, **kwargs):
        if self.pk is None:
            n_suppliers = Supplier.objects.all().count()
            #will overwrite if error occurs
            self.account = Account.objects.create(
                name= "Supplier: %s" % self.name,
                id = 2100 + n_suppliers,
                balance =0,
                type = 'liability',
                description = 'Account which represents debt owed to a supplier',
                balance_sheet_category='current-liabilities'
            )
        
        super(Supplier, self).save(*args, **kwargs)



class UnitOfMeasure(models.Model):
    '''Class for arepresenting units of inventory.
    can be a base unit where no calculations are required.
    can also be a derived unit where the quantity is calculated back into the base unit for each element.'''
    name = models.CharField(max_length=64)
    description = models.TextField(default="")
    is_derived = models.BooleanField(default = False)
    base_unit = models.ForeignKey('inventory.UnitOfMeasure', null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DerivedUnitStage(models.Model):
    OPERATIONS = [
        (0, 'sum'),
        (1, 'difference'),
        (2, 'product'),
        (3, 'ratio')
        ]
    stage_number = models.PositiveSmallIntegerField()
    operation = models.PositiveSmallIntegerField(choices=OPERATIONS)
    value = models.FloatField()
    unit = models.ForeignKey('inventory.UnitOfMeasure')

class Category(models.Model):
    '''Used to organize inventory'''
    name = models.CharField(max_length=64)
    parent = models.ForeignKey('inventory.Category', blank=True, null=True)
    description = models.TextField(default="")

    def __str__(self):
        return self.name

    @property
    def items(self):
        return Product.objects.filter(category=self)

    @property
    def children(self):
        return self.category_set.all()
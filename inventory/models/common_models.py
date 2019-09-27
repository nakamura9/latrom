# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from decimal import Decimal as D

import rest_framework
from django.conf import settings
from django.db import models
from django.db.models import Q

from accounting.models import Account, Journal, JournalEntry
from common_data.models import SingletonModel, SoftDeletionModel
from inventory.models.item import InventoryItem
from inventory.schedules import run_inventory_service
from background_task.models import Task
from django.shortcuts import reverse


class InventorySettings(SingletonModel):
    INVENTORY_VALUATION_PERIOD=[
        (30, 'Month'),
        (90, 'Quarter'),
        (182, 'Six Months'),
        (365, 'One Year')
    ]
    INVENTORY_VALUATION_METHODS = [
        (1, 'Averaging'),
    ]
    PRICING_METHODS = [
        (1, 'Direct Pricing'),
        (2, 'Margin'),
        (3, 'Markup')
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
    default_product_sales_pricing_method= models.PositiveSmallIntegerField(
        choices=PRICING_METHODS, default=1
    )
    inventory_check_frequency = models.PositiveSmallIntegerField(
        choices=INVENTORY_CHECK_FREQUENCY, default=1
    )
    inventory_check_date = models.PositiveSmallIntegerField(
        choices=INVENTORY_CHECK_DATE, default=1
    )
    use_warehousing_model = models.BooleanField(default=True)
    use_storage_media_model = models.BooleanField(default=True)
    use_product_inventory = models.BooleanField(default=True)
    use_equipment_inventory = models.BooleanField(default=True)
    use_consumables_inventory = models.BooleanField(default=True)
    use_raw_materials_inventory = models.BooleanField(default=True)
    #TODO capitalization_limit = models.DecimalField(max_digits=16, decimal_places=2)
    is_configured = models.BooleanField(default=False)
    service_hash = models.CharField(max_length=255, default="", blank=True)


class InventoryController(models.Model):
    '''Model that represents employees with the role of 
    inventory controller and have the ability to make purchase orders,
    receive them, transfer inventory between warehouses and perform other 
    functions.'''
    employee = models.OneToOneField('employees.Employee', on_delete=models.SET_NULL, null=True, 
        limit_choices_to=Q(user__isnull=False))
    can_authorize_equipment_requisitions = models.BooleanField(default=False)
    can_authorize_consumables_requisitions = models.BooleanField(default=False)

    def __str__(self):
        return self.employee.full_name




class UnitOfMeasure(SoftDeletionModel):
    '''Class for arepresenting units of inventory.
    can be a base unit where no calculations are required.
    can also be a derived unit where the quantity is calculated back into the base unit for each element.'''
    name = models.CharField(max_length=64)
    description = models.TextField(default="")
    eval_string = models.CharField(max_length=255, default="")
    is_derived = models.BooleanField(default = False)
    base_unit = models.ForeignKey('inventory.UnitOfMeasure', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def derived_units(self):
        return UnitOfMeasure.objects.filter(base_unit=self)

    def get_absolute_url(self):
        return reverse("inventory:unit-detail", kwargs={"pk": self.pk})
    

class Category(models.Model):
    '''Used to organize inventory'''
    name = models.CharField(max_length=64)
    parent = models.ForeignKey('inventory.Category', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(default="")

    def get_absolute_url(self):
        return reverse("inventory:category-detail", kwargs={"pk": self.pk})
    

    def __str__(self):
        return self.name

    @property
    def items(self):
        #deprecating
        return InventoryItem.objects.filter(category=self)

    @property
    def children(self):
        return Category.objects.filter(parent=self)

    @property
    def siblings(self):
        if not self.parent:
            return Category.objects.filter(parent__isnull=True).exclude(
                pk=self.pk)
        else:
            return Category.objects.filter(parent=self.parent).exclude(
                pk=self.pk) 
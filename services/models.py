# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Service(models.Model):
    # client and sales facing model
    name = models.CharField(max_length=255)
    description = models.TextField()
    flat_fee = models.DecimalField(max_digits=6, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    

    def create_work_order(self):
        pass

    def __str__(self):
        return self.name

#internal facing models 
'''
class ScheduledWorkOrder(models.Model):
    consumables = models.ForeignKey('inventory.Item')
    equipment = models.ForeignKey('accounting.Asset')
    

class UnScheduledWorkOrder(models.Model):
    pass

class Technician(models.Model):
    employee = models.ForeignKey('employees.Employee')


'''
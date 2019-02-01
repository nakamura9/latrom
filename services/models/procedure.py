# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from common_data.utilities import time_choices


class Task(models.Model):
    procedure = models.ForeignKey('services.ServiceProcedure', 
        on_delete=models.CASCADE)
    description = models.TextField()
    
    def __str__(self):
        return self.description


class ServiceProcedure(models.Model):
    as_checklist = models.BooleanField(default=False, blank=True)
    name = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    required_equipment = models.ManyToManyField('inventory.Equipment', blank=True)
    required_consumables = models.ManyToManyField('inventory.Consumable', blank=True)

    @property
    def steps(self):
        return self.task_set.all().order_by('pk')

    def __str__(self):
        return self.name
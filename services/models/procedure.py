# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from common_data.utilities import time_choices
from django.shortcuts import reverse

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
    author = models.ForeignKey('auth.user', null=True,  
        on_delete=models.SET_NULL)
    description = models.TextField(blank=True)
    required_equipment = models.ManyToManyField('inventory.InventoryItem',
        related_name="equipment", 
        blank=True)
    required_consumables = models.ManyToManyField('inventory.InventoryItem', 
        related_name="consumables", 
        blank=True)

    def get_absolute_url(self):
        return reverse("services:procedure-details", kwargs={"pk": self.pk})
    

    @property
    def steps(self):
        return self.task_set.all().order_by('pk')

    def __str__(self):
        return self.name
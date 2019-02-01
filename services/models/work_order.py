# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.db.models import Q
from common_data.utilities import time_choices


class WorkOrderRequest(models.Model):
    invoice_type = models.PositiveSmallIntegerField(choices=[
        (0, 'Service Invoice'),
        (1, 'Combined Invoice')
    ])
    service_invoice = models.OneToOneField('invoicing.serviceinvoice', 
        blank=True, null=True, on_delete=models.SET_NULL)
    combined_invoice = models.OneToOneField('invoicing.combinedinvoice',
        blank=True, null=True, on_delete=models.SET_NULL)
    service = models.ForeignKey('services.service', null=True, 
        on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=[
        ('request', 'Requested'),
        ('in-progress', 'In Progress'),
        ('completed', 'Completed'),
        ])


    @property
    def invoice(self):
        return self.service_invoice if self.invoice_type == 0 else \
            self.combined_invoice

    @property
    def work_orders(self):
        return self.serviceworkorder_set.all()

class ServiceWorkOrder(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('progress', 'In progress'),
        ('completed', 'Completed'),
        ('authorized', 'Authorized'),
        ('declined', 'Declined')
        ]
    date = models.DateField()
    time = models.TimeField(choices = time_choices(
        '06:00:00', '18:30:00', '00:30:00'
        ))
    # for services done within the organization
    internal = models.BooleanField(default=False)
    
    works_request = models.ForeignKey('services.workorderrequest', 
        blank=True, null=True, on_delete=models.SET_NULL)

    description = models.TextField(blank=True, default="")
    completed = models.DateTimeField(null=True, blank=True)
    expected_duration = models.DurationField(choices = time_choices(
        '00:00:00', '08:00:00', '00:30:00', delta=True
        ), null=True, blank=True) 
    actual_duration = models.DurationField(choices = time_choices(
        '00:00:00', '08:00:00', '00:30:00', delta=True
        ), null=True, blank=True)
    service_people = models.ManyToManyField('services.ServicePerson', 
        blank=True)
    team = models.ForeignKey('services.ServiceTeam', on_delete=models.SET_NULL, null=True, 
        blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, blank=True)
    authorized_by = models.ForeignKey('employees.Employee', 
        on_delete=models.CASCADE, null=True, 
        blank=True,
        limit_choices_to=Q(user__isnull=False))#filter queryset
    comments = models.TextField(blank=True)

    def __str__(self):
        return "WO{}".format(self.pk) #TODO string padding

    @property
    def procedure_pk(self):
        print(self.works_request.service.procedure.pk)
        return self.works_request.service.procedure.pk

class WorkOrderExpense(models.Model):
    work_order = models.ForeignKey('services.ServiceWorkOrder', 
        on_delete=models.SET_NULL, null=True) 
    expense = models.ForeignKey('accounting.Expense', 
        on_delete=models.SET_NULL, null=True)

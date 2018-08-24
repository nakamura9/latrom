# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import  UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django_filters.views import FilterView
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from inventory import forms
from inventory import models
from inventory import serializers
from inventory import filters
from common_data.utilities import *
from common_data.models import GlobalConfig 
from invoicing.models import SalesConfig

from .common import CREATE_TEMPLATE, InventoryControllerCheckMixin


class SupplierCreateView(InventoryControllerCheckMixin, ExtraContext, CreateView):
    form_class = forms.SupplierForm
    model = models.Supplier
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE
    extra_context = {"title": "Create New Supplier"}


class SupplierUpdateView(InventoryControllerCheckMixin, ExtraContext, 
        UpdateView):
    form_class = forms.SupplierForm
    model = models.Supplier
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE
    extra_context = {"title": "Update Existing Supplier"}


class SupplierListView(InventoryControllerCheckMixin, ExtraContext, FilterView):
    paginate_by = 10
    filterset_class = filters.SupplierFilter
    template_name = os.path.join("inventory", "supplier", "list.html")
    extra_context = {"title": "Supplier List",
                    "new_link": reverse_lazy("inventory:supplier-create")}

    def get_queryset(self):
        return models.Supplier.objects.all().order_by('pk')


class SupplierDeleteView(InventoryControllerCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url=reverse_lazy('inventory:supplier-list')
    model = models.Supplier

class SupplierListAPIView(ListAPIView):
    serializer_class = serializers.SupplierSerializer
    queryset = models.Supplier.objects.all()
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from common_data.models import GlobalConfig
from common_data.utilities import *
from common_data.views import PaginationMixin
from inventory import filters, forms, models, serializers
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


class SupplierListView(InventoryControllerCheckMixin, ExtraContext, PaginationMixin, FilterView):
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

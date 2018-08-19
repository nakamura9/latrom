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

from common import CREATE_TEMPLATE, InventoryControllerCheckMixin

class ProductAPIView(ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer


class ProductDeleteView(InventoryControllerCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.Product
    success_url = reverse_lazy('inventory:product-list')


class ProductUpdateView(InventoryControllerCheckMixin, ExtraContext, UpdateView):
    form_class = forms.ProductUpdateForm
    model = models.Product
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE
    extra_context = {"title": "Update Existing Product"}


class ProductDetailView(InventoryControllerCheckMixin, DetailView):
    model = models.Product
    template_name = os.path.join("inventory", "item", "detail.html")


class ProductListView(InventoryControllerCheckMixin, ExtraContext, FilterView):
    paginate_by = 10
    filterset_class = filters.ProductFilter
    template_name = os.path.join('inventory', 'item', 'list.html')
    extra_context = {
        'title': 'Product List',
        "new_link": reverse_lazy("inventory:product-create")
    }

    def get_queryset(self):
        return models.Product.objects.all().order_by('pk')


class ProductCreateView(InventoryControllerCheckMixin, ExtraContext, CreateView):
    form_class = forms.ProductForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Create New Product",
        "modals": [Modal(**{
            'title': 'Add Unit',
            'action': reverse_lazy('inventory:unit-create'),
            'form': forms.UnitForm
        }),
        Modal(**{
            'title': 'Add Supplier',
            'action': reverse_lazy('inventory:supplier-create'),
            'form': forms.SupplierForm
        }),
        Modal(**{
            'title': 'Add Category',
            'action': reverse_lazy('inventory:category-create'),
            'form': forms.CategoryForm
        })]
        }


class QuickProductCreateView(InventoryControllerCheckMixin, 
        ExtraContext, CreateView):
    form_class = forms.QuickProductForm
    model = models.Product
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")


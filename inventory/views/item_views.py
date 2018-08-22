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
    template_name = os.path.join("inventory", "item", "product", "detail.html")


class ProductListView(InventoryControllerCheckMixin, ExtraContext, FilterView):
    paginate_by = 10
    filterset_class = filters.ItemFilter
    template_name = os.path.join('inventory', 'item', "product", 'list.html')
    extra_context = {
        'title': 'Product List',
        "new_link": reverse_lazy("inventory:product-create")
    }

    def get_queryset(self):
        return models.Product.objects.all().order_by('pk')


class ProductCreateView(InventoryControllerCheckMixin, ExtraContext, 
        CreateView):
    form_class = forms.ProductForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Create New Product",
        }


class QuickProductCreateView(InventoryControllerCheckMixin, 
        ExtraContext, CreateView):
    form_class = forms.QuickProductForm
    model = models.Product
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")

################################################
#               Consumable                     #
################################################

class ConsumableAPIView(ModelViewSet):
    queryset = models.Consumable.objects.all()
    serializer_class = serializers.ConsumableSerializer


class ConsumableUpdateView(InventoryControllerCheckMixin, ExtraContext,
        UpdateView):
    form_class = forms.ConsumableForm
    model = models.Consumable
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE
    extra_context = {"title": "Update Existing Consumable Inventory"}


class ConsumableDetailView(InventoryControllerCheckMixin, DetailView):
    model = models.Consumable
    template_name = os.path.join("inventory", "item", 'consumable',"detail.html")


class ConsumableListView(InventoryControllerCheckMixin, ExtraContext, 
        FilterView):
    paginate_by = 10
    filterset_class = filters.ItemFilter
    template_name = os.path.join('inventory', 'item', 'consumable','list.html')
    extra_context = {
        'title': 'Consumable List',
        "new_link": reverse_lazy("inventory:consumable-create")
    }

    def get_queryset(self):
        return models.Consumable.objects.all().order_by('pk')


class ConsumableCreateView(InventoryControllerCheckMixin, ExtraContext, 
        CreateView):
    form_class = forms.ConsumableForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Create New Consumable",
        }

####################################################
#                   Equipment Views                #
####################################################


class EquipmentAPIView(ModelViewSet):
    queryset = models.Equipment.objects.all()
    serializer_class = serializers.EquipmentSerializer


class EquipmentUpdateView(InventoryControllerCheckMixin, ExtraContext, 
        UpdateView):
    form_class = forms.EquipmentForm
    model = models.Equipment
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE
    extra_context = {"title": "Update Existing Equipment Details"}


class EquipmentDetailView(InventoryControllerCheckMixin, DetailView):
    model = models.Equipment
    template_name = os.path.join("inventory", "item", 'equipment', "detail.html")


class EquipmentListView(InventoryControllerCheckMixin, ExtraContext, 
        FilterView):
    paginate_by = 10
    filterset_class = filters.ItemFilter
    template_name = os.path.join('inventory', 'item', 'equipment', 'list.html')
    extra_context = {
        'title': 'Equipment List',
        "new_link": reverse_lazy("inventory:equipment-create")
    }

    def get_queryset(self):
        return models.Equipment.objects.all().order_by('pk')


class EquipmentCreateView(InventoryControllerCheckMixin, ExtraContext, 
        CreateView):
    form_class = forms.EquipmentForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Add New Equipment",
        }
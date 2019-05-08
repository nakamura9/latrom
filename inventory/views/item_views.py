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
from services.models import EquipmentRequisition

from .common import CREATE_TEMPLATE


class ProductAPIView(ModelViewSet):
    queryset = models.InventoryItem.objects.filter(type=0)
    serializer_class = serializers.InventoryItemSerializer


class ProductDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.InventoryItem
    success_url = reverse_lazy('inventory:product-list')


class ProductUpdateView( ContextMixin, UpdateView):
    form_class = forms.ProductForm
    model = models.InventoryItem
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {"title": "Update Existing Product"}
    
    def get_initial(self):
        return {
            'tax': self.object.tax
        }

class ProductDetailView( DetailView):
    model = models.InventoryItem
    template_name = os.path.join("inventory", "item", "product", "detail.html")


class ProductListView( ContextMixin, PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryItemFilter
    template_name = os.path.join('inventory', 'item', "product", 'list.html')
    extra_context = {
        'title': 'Product List',
        "new_link": reverse_lazy("inventory:product-create")
    }

    def get_queryset(self):
        return models.InventoryItem.objects.filter(type=0).order_by('pk')


class ProductCreateView( ContextMixin, 
        CreateView):
    form_class = forms.ProductForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Create New Product",
        'description': 'Cycle  through the tabs to enter information regarding product description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Add Vendor',
            'url': '/inventory/supplier/create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        },]
        }

    def get_initial(self):
        return {
            'type': 0 #for product
        }

################################################
#               Consumable                     #
################################################

class ConsumableAPIView(ModelViewSet):
    queryset = models.InventoryItem.objects.filter(type=2)
    serializer_class = serializers.InventoryItemSerializer


class ConsumableUpdateView( ContextMixin,
        UpdateView):
    form_class = forms.ConsumableForm
    model = models.InventoryItem
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {"title": "Update Existing Consumable Inventory"}


class ConsumableDetailView( DetailView):
    model = models.InventoryItem
    template_name = os.path.join("inventory", "item", 'consumable',"detail.html")


class ConsumableListView( ContextMixin, 
        PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryItemFilter
    template_name = os.path.join('inventory', 'item', 'consumable','list.html')
    extra_context = {
        'title': 'Consumable List',
        "new_link": reverse_lazy("inventory:consumable-create")
    }

    def get_queryset(self):
        return models.InventoryItem.objects.filter(type=2).order_by('pk')


class ConsumableCreateView( ContextMixin, 
        CreateView):
    form_class = forms.ConsumableForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Create New Consumable",
        'description': 'Cycle  through the tabs to enter information regarding consumable description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Add Vendor',
            'url': '/inventory/supplier/create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        }],
        }
    
    def get_initial(self):
        return {
            'type': 2 #for consumables
        }

####################################################
#                   Equipment Views                #
####################################################


class EquipmentAPIView(ModelViewSet):
    queryset = models.InventoryItem.objects.filter(type=1)
    serializer_class = serializers.InventoryItemSerializer


class EquipmentUpdateView( ContextMixin, 
        UpdateView):
    form_class = forms.EquipmentForm
    model = models.InventoryItem
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {"title": "Update Existing Equipment Details"}

    def get_initial(self):
        initial = super().get_initial()
        item = models.InventoryItem.objects.get(pk=self.kwargs['pk'])
        if item.equipment_component.asset_data:
            initial['asset_data'] = item.equipment_component.asset_data.pk
        return initial
        
class EquipmentDetailView( DetailView):
    model = models.InventoryItem
    template_name = os.path.join("inventory", "item", 'equipment', "detail.html")


class EquipmentListView( ContextMixin, 
        PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryItemFilter
    template_name = os.path.join('inventory', 'item', 'equipment', 'list.html')
    extra_context = {
        'title': 'Equipment List',
        "new_link": reverse_lazy("inventory:equipment-create")
    }

    def get_queryset(self):
        return models.InventoryItem.objects.filter(type=1).order_by('pk')


class EquipmentCreateView( ContextMixin, 
        CreateView):
    form_class = forms.EquipmentForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Add New Equipment",
        'description': 'Cycle  through the tabs to enter information regarding equipment description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Add Vendor',
            'url': '/inventory/supplier/create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        }],
        }

    def get_initial(self):
        return {
            'type': 1# for equipment
        }

####################################################
#                Raw Material Views                #
####################################################


class RawMaterialAPIView(ModelViewSet):
    queryset = models.InventoryItem.objects.all()
    serializer_class = serializers.InventoryItemSerializer


class RawMaterialUpdateView( ContextMixin, 
        UpdateView):
    form_class = forms.ConsumableForm# TODO make a raw material form
    model = models.InventoryItem
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE
    extra_context = {"title": "Update Existing Raw Materials Details"}


class RawMaterialDetailView( DetailView):
    model = models.InventoryItem
    template_name = os.path.join("inventory", "item", 'raw_material', "detail.html")


class RawMaterialListView( ContextMixin, 
        PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryItemFilter
    template_name = os.path.join('inventory', 'item', 'raw_material', 'list.html')
    extra_context = {
        'title': 'RawMaterial List',
        "new_link": reverse_lazy("inventory:raw-material-create")
    }

    def get_queryset(self):
        return models.InventoryItem.objects.all().order_by('pk')


class RawMaterialCreateView( ContextMixin, 
        CreateView):
    form_class = forms.ConsumableForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Add New Raw Material",
        'description': 'Cycle  through the tabs to enter information regarding material description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Add Vendor',
            'url': '/inventory/supplier/create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        }],
        }

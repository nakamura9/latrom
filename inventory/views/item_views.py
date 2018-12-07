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


class ProductListView(InventoryControllerCheckMixin, ExtraContext, PaginationMixin, FilterView):
    paginate_by = 10
    filterset_class = filters.ProductFilter
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
        'description': 'Cycle  through the tabs to enter information regarding product description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Create Supplier',
            'url': '/inventory/supplier-create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        },]
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
        PaginationMixin, FilterView):
    paginate_by = 10
    filterset_class = filters.ConsumableFilter
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
        'description': 'Cycle  through the tabs to enter information regarding consumable description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Create Supplier',
            'url': '/inventory/supplier-create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        }],
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
        PaginationMixin, FilterView):
    paginate_by = 10
    filterset_class = filters.EquipmentFilter
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
        'description': 'Cycle  through the tabs to enter information regarding equipment description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Create Supplier',
            'url': '/inventory/supplier-create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        }],
        }


####################################################
#                Raw Material Views                #
####################################################


class RawMaterialAPIView(ModelViewSet):
    queryset = models.RawMaterial.objects.all()
    serializer_class = serializers.RawMaterialSerializer


class RawMaterialUpdateView(InventoryControllerCheckMixin, ExtraContext, 
        UpdateView):
    form_class = forms.RawMaterialForm
    model = models.RawMaterial
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE
    extra_context = {"title": "Update Existing Raw Materials Details"}


class RawMaterialDetailView(InventoryControllerCheckMixin, DetailView):
    model = models.RawMaterial
    template_name = os.path.join("inventory", "item", 'raw_material', "detail.html")


class RawMaterialListView(InventoryControllerCheckMixin, ExtraContext, 
        PaginationMixin, FilterView):
    paginate_by = 10
    filterset_class = filters.RawMaterialFilter
    template_name = os.path.join('inventory', 'item', 'raw_material', 'list.html')
    extra_context = {
        'title': 'RawMaterial List',
        "new_link": reverse_lazy("inventory:raw-material-create")
    }

    def get_queryset(self):
        return models.RawMaterial.objects.all().order_by('pk')


class RawMaterialCreateView(InventoryControllerCheckMixin, ExtraContext, 
        CreateView):
    form_class = forms.RawMaterialForm
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Add New Raw Material",
        'description': 'Cycle  through the tabs to enter information regarding material description, quantity, dimensions and pricing. ',
        'related_links': [{
            'name': 'Create Supplier',
            'url': '/inventory/supplier-create/'
        },{
            'name': 'Add Unit',
            'url': '/inventory/unit-create/'
        },{
            'name': 'Add Inventory Category',
            'url': '/inventory/category-create/'
        }],
        }

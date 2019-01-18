# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from inventory.views.util import InventoryConfigMixin 
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

CREATE_TEMPLATE =os.path.join("common_data", "create_template.html")


#####################################################
#               Inventory Controller                #
#####################################################


class InventoryControllerCreateView(ContextMixin, CreateView):
    form_class = forms.InventoryControllerForm
    template_name = CREATE_TEMPLATE
    success_url =  reverse_lazy('inventory:inventory-controller-list')
    extra_context = {
        'title': 'Create Inventory Controller',
        'description': 'Assign an existing employee to the role of inventory controller and provide the permissions for their role.',
        'related_links': [{
            'name': 'Create Employee',
            'url': '/employees/create-employee/'
        }]
    }
    
class InventoryControllerUpdateView(ContextMixin, UpdateView):
    form_class = forms.InventoryControllerUpdateForm
    template_name = CREATE_TEMPLATE
    queryset = models.InventoryController.objects.all()
    success_url =  reverse_lazy('inventory:inventory-controller-list')
    extra_context = {
        'title': 'Update Inventory Controller',
        
    }

class InventoryControllerListView(ContextMixin,   PaginationMixin, FilterView):
    queryset = models.InventoryController.objects.all()
    template_name = os.path.join('inventory', 'inventory_controller_list.html')
    filterset_class = filters.ControllerFilter
    extra_context = {
        'title': 'List of Inventory Controllers',
        'new_link': reverse_lazy('inventory:create-inventory-controller'),
        'description': 'These are employees with user privileges assigned to manage inventory creation, movement and verification.'
    }


class InventoryDashboard( 
    InventoryConfigMixin, 
    TemplateView):
    template_name = os.path.join("inventory", "dashboard.html")


#######################################################
#                       Units                         #
#######################################################


class UnitCreateView(ContextMixin,  CreateView):
    form_class = forms.UnitForm
    model = models.UnitOfMeasure
    success_url = reverse_lazy('inventory:unit-list')
    template_name = CREATE_TEMPLATE
    extra_context = {
        'title':'Create New Unit of measure'
    }

class UnitUpdateView(ContextMixin,  UpdateView):
    form_class = forms.UnitForm
    model = models.UnitOfMeasure
    success_url = reverse_lazy('inventory:unit-list')
    template_name = CREATE_TEMPLATE
    extra_context = {
        'title':'Update Unit of measure'
    }

class UnitDetailView( DetailView):
    model = models.UnitOfMeasure
    template_name = os.path.join('inventory', 'unit', 'detail.html')


class UnitListView(ContextMixin,  PaginationMixin, FilterView):
    filterset_class = filters.UnitFilter
    model = models.UnitOfMeasure
    paginate_by = 10
    template_name = os.path.join('inventory', 'unit', 'list.html')
    extra_context = {
        'title': 'List of Units',
        'new_link': reverse_lazy('inventory:unit-create')
    }


class UnitDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.UnitOfMeasure
    success_url = reverse_lazy('invoicing.product-list')

class UnitAPIView(ModelViewSet):
    serializer_class = serializers.UnitSerializer
    queryset = models.UnitOfMeasure.objects.all()

class ConfigView( UpdateView):
    template_name = os.path.join('inventory', 'config.html')
    form_class = forms.ConfigForm
    model = models.InventorySettings
    success_url = reverse_lazy('inventory:home')
    #change this page

class CategoryCreateView( CreateView):
    form_class = forms.CategoryForm
    model = models.Category
    success_url = reverse_lazy('inventory:category-list')
    template_name = os.path.join('inventory', 'category', 'create.html')

class CategoryUpdateView( UpdateView):
    form_class = forms.CategoryForm
    model = models.Category
    success_url = reverse_lazy('inventory:category-list')
    template_name = os.path.join('inventory', 'category','update.html')

class CategoryListView( TemplateView):
    template_name = os.path.join('inventory', 'category', 'list.html')

class CategoryDetailView( DetailView):
    template_name = os.path.join('inventory', 'category', 'detail.html')
    model = models.Category

class CategoryListAPIView(ListAPIView):
    serializer_class = serializers.CategorySerializer

    def get_queryset(self):
        return models.Category.objects.filter(parent=None)

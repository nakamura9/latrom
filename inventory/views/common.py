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

CREATE_TEMPLATE =os.path.join("common_data", "create_template.html")


#####################################################
#               Inventory Controller                #
#####################################################
class InventoryControllerCheckMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif hasattr(self.request.user, 'employee') and \
                self.request.user.employee.is_inventory_controller:
            return True
        else:
            return False


class InventoryControllerCreateView(ExtraContext, CreateView):
    form_class = forms.InventoryControllerForm
    template_name = CREATE_TEMPLATE
    success_url =  reverse_lazy('inventory:inventory-controller-list')
    extra_context = {
        'title': 'Assign new Inventory Controller'
    }
    

class InventoryControllerListView(ExtraContext, ListView):
    queryset = models.InventoryController.objects.all()
    template_name = os.path.join('inventory', 'inventory_controller_list.html')
    extra_context = {
        'title': 'List of Inventory Controllers',
        'new_link': reverse_lazy('inventory:create-inventory-controller')
    }


class InventoryDashboard(InventoryControllerCheckMixin, TemplateView):
    template_name = os.path.join("inventory", "dashboard.html")


#######################################################
#                       Units                         #
#######################################################


class UnitCreateView(InventoryControllerCheckMixin, CreateView):
    form_class = forms.UnitForm
    model = models.UnitOfMeasure
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE


class UnitDeleteView(InventoryControllerCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.UnitOfMeasure
    success_url = reverse_lazy('invoicing.item-list')

class ConfigView(InventoryControllerCheckMixin, UpdateView):
    template_name = os.path.join('inventory', 'config.html')
    form_class = forms.ConfigForm
    model = models.InventorySettings
    success_url = reverse_lazy('inventory:home')
    #change this page

class CategoryCreateView(InventoryControllerCheckMixin, CreateView):
    form_class = forms.CategoryForm
    model = models.Category
    success_url = reverse_lazy('inventory:home')
    template_name = CREATE_TEMPLATE
    extra_context = {"title": "Category"}
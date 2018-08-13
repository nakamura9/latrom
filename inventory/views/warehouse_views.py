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


class WareHouseCreateView(ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.WareHouseForm
    success_url = reverse_lazy('inventory:warehouse-list')
    extra_context = {
        'title': 'Create New Warehouse Location'
    }


class WareHouseUpdateView(ExtraContext, UpdateView):
    template_name = CREATE_TEMPLATE
    model = models.WareHouse
    form_class = forms.WareHouseForm
    success_url = reverse_lazy('inventory:warehouse-list')
    extra_context = {
        'title': 'Update Warehouse Location Details'
    }


class WareHouseDetailView( DetailView):
    template_name = os.path.join('inventory', 'warehouse', 'detail.html')
    model = models.WareHouse


class WareHouseListView(ExtraContext, ListView):
    template_name = os.path.join('inventory', 'warehouse', 'list.html')
    model = models.WareHouse
    paginate_by = 10
    extra_context = {
        'new_link': reverse_lazy('inventory:warehouse-create'),
        'title': 'List of Inventory WareHouse Locations'
    }


class WareHouseDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.WareHouse
    success_url = reverse_lazy('inventory:warehouse-list')


class WareHouseItemAPIView(RetrieveAPIView):
    serializer_class = serializers.WareHouseItemSerializer
    queryset = models.WareHouseItem.objects.all()


class WareHouseItemListAPIView(ListAPIView):
    serializer_class = serializers.WareHouseItemSerializer
    pagination_class = WareHousePaginator
    
    def get_queryset(self):
        w_pk = self.kwargs['warehouse']
        warehouse = get_object_or_404(models.WareHouse, pk=w_pk)
        return models.WareHouseItem.objects.filter(
            warehouse=warehouse)


class UnpaginatedWareHouseItemListAPIView(ListAPIView):
    serializer_class = serializers.WareHouseItemSerializer
    
    def get_queryset(self):
        w_pk = self.kwargs['warehouse']
        warehouse = get_object_or_404(models.WareHouse, pk=w_pk)
        return models.WareHouseItem.objects.filter(
            warehouse=warehouse)


class WareHouseAPIView(ModelViewSet):
    queryset = models.WareHouse.objects.all()
    serializer_class = serializers.WareHouseSerializer

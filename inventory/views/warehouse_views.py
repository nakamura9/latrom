# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.contrib.auth.decorators import login_required
from inventory.views.util import InventoryConfigMixin 
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination


from common_data.models import GlobalConfig
from common_data.utilities import *
from inventory import filters, forms, models, serializers
from invoicing.models import SalesConfig

from .common import CREATE_TEMPLATE


class WareHouseCreateView(ContextMixin, CreateView):
    template_name = os.path.join('common_data','crispy_create_template.html')
    form_class = forms.WareHouseForm
    extra_context = {
        'title': 'Create  Warehouse',
        'description': 'Register a new location as a warehouse for storing inventory. Further detail regarding inventory location is provided by the storage media model.'
    }


class WareHouseUpdateView(ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    model = models.WareHouse
    form_class = forms.WareHouseForm
    extra_context = {
        'title': 'Update Warehouse Location Details'
    }

class WareHouseItemListView(ListView):
    template_name = os.path.join('inventory', 'warehouse', 'item_list.html')
    paginate_by = 20
    def get_queryset(self):
        return models.WareHouseItem.objects.filter(
            warehouse=models.WareHouse.objects.get(pk=self.kwargs['pk']))


class WareHouseDetailView(InventoryConfigMixin, DetailView):
    template_name = os.path.join('inventory', 'warehouse', 'detail.html')
    model = models.WareHouse


class WareHouseListView(ContextMixin, ListView):
    template_name = os.path.join('inventory', 'warehouse', 'list.html')
    model = models.WareHouse
    paginate_by = 20
    extra_context = {
        'new_link': reverse_lazy('inventory:warehouse-create'),
        'title': 'List of  Warehouses'
    }


class WareHouseDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.WareHouse
    success_url = reverse_lazy('inventory:warehouse-list')


class WareHouseItemAPIView(RetrieveAPIView):
    serializer_class = serializers.WareHouseItemSerializer
    queryset = models.WareHouseItem.objects.all()


class WareHousePaginator(PageNumberPagination):
    page_size = 10
    max_page_size = 10
    page_size_query_description = 'page_size'

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

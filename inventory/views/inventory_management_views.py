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

#######################################################
#               Inventory Check Views                 #
#######################################################


class InventoryCheckCreateView(CreateView):
    template_name = os.path.join('inventory', 'inventory_check', 'create.html')
    form_class = forms.InventoryCheckForm
    success_url = reverse_lazy('inventory:warehouse-list') 
    
    def get_initial(self):
        return {
            'warehouse': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        resp = super(InventoryCheckCreateView, self).post(
            request, *args, **kwargs)
        if not self.object:
            return resp
        
        raw_data = request.POST['adjustments']
        adjustments = json.loads(urllib.unquote(raw_data))
        for adj in adjustments:
            wh_item = models.WareHouseItem.objects.get(pk=adj['warehouse_item'])
            models.StockAdjustment.objects.create(
                warehouse_item = wh_item,
                inventory_check = self.object,
                note = adj['note'],
                adjustment = adj['adjustment']
            )

        return resp


class InventoryCheckDetailView(DetailView):
    model = models.InventoryCheck
    template_name = os.path.join('inventory', 'inventory_check', 'summary.html')

class InventoryCheckListView(ExtraContext ,FilterView):
    paginate_by = 10
    filterset_class = filters.InventoryCheckFilter
    template_name = os.path.join("inventory", "inventory_check', 'list.html")
    extra_context = {"title": "List of Inventory Checks",
                    "new_link": reverse_lazy("inventory:inventory-check-form")}

    def get_queryset(self):
        return models.InventoryCheck.objects.all().order_by('date')


class StockAdjustmentAPIView(ModelViewSet):
    queryset = models.StockAdjustment.objects.all()
    serializer_class = serializers.StockAdjustmentSerializer


#######################################################
#               Transfer Order Views                  #
#######################################################


class TransferOrderCreateView(CreateView):
    template_name = os.path.join('inventory', 'transfer', 'create.html')
    form_class = forms.TransferOrderForm
    success_url = reverse_lazy('inventory:home')

    def post(self, request, *args, **kwargs):
        resp = super(TransferOrderCreateView, self).post(
            request, *args, **kwargs)
        print request.POST['items']
        data = json.loads(urllib.unquote(request.POST['items']))
        items = data['items'] 
        for i in items:
            item = models.Item.objects.get(pk=i['item'].split('-')[0])
            models.TransferOrderLine.objects.create(
                item = item,
                quantity = i['quantity'],
                transfer_order = self.object
            )
        return resp

class TransferOrderListView(ExtraContext, FilterView):
    filterset_class = filters.TransferOrderFilter
    template_name = os.path.join('inventory', 'transfer', 'list.html')
    paginate_by =10
    extra_context = {
        'title': 'List of Transfer Orders',
        'new_link': reverse_lazy('inventory:create-transfer-order')
    }

class TransferOrderDetailView(DetailView):
    model = models.TransferOrder
    template_name = os.path.join('inventory', 'transfer', 'detail.html')


class TransferOrderReceiveView(ExtraContext, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.TransferReceiptForm
    model = models.TransferOrder
    success_url = reverse_lazy('inventory:home')
    extra_context = {
        'title': 'Receive Transfer of Inventory'
    }


    def post(self, request, *args, **kwargs):
        resp = super(TransferOrderReceiveView, self).post(request, *args, **kwargs)

        self.object.complete()
        return resp

#######################################################
#               Goods Received Views                  #
#######################################################

class StockReceiptCreateView(InventoryControllerCheckMixin,CreateView):
    form_class = forms.StockReceiptForm
    model = models.StockReceipt
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("inventory", "goods_received",
        "stock_receipt.html")
    extra_context = {"title": "Receive Ordered goods"}

    def get_initial(self):
        return {
            'order': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        resp = super(StockReceiptCreateView, self).post(request, *args, **kwargs)
        data = json.loads(urllib.unquote(request.POST['received-items']))
        for key in data.keys():
            _ , pk = key.split('-')
            models.OrderItem.objects.get(pk=pk).receive(data[key])
            
        #make transaction after receiving each item.
        self.object.create_entry()
        return resp 

class GoodsReceivedVoucherView(InventoryControllerCheckMixin, DetailView):
    model = models.StockReceipt
    template_name = os.path.join("inventory", "goods_received", "voucher.html")

    def get_context_data(self, *args, **kwargs):
        context = super(GoodsReceivedVoucherView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        return apply_style(context)

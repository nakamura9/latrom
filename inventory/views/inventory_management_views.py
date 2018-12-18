# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
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

#######################################################
#               Inventory Check Views                 #
#######################################################


class InventoryCheckCreateView(CreateView):
    '''
    Also Known as stock take. Used to compare actual inventory versus recorded inventory. Each item in a warehouse is examined and verified. 
    Changes are made to each warehouse based on data recorded here.
    '''
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
        adjustments = json.loads(urllib.parse.unquote(raw_data))
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

class InventoryCheckListView(ExtraContext ,PaginationMixin, FilterView):
    paginate_by = 10
    filterset_class = filters.InventoryCheckFilter
    template_name = os.path.join("inventory", "inventory_check", 'list.html')
    extra_context = {"title": "List of Inventory Checks"}

    def get_queryset(self):
        w = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return models.InventoryCheck.objects.filter(warehouse=w).order_by('date')


class StockAdjustmentAPIView(ModelViewSet):
    queryset = models.StockAdjustment.objects.all()
    serializer_class = serializers.StockAdjustmentSerializer


#######################################################
#               Transfer Order Views                  #
#######################################################


class TransferOrderCreateView(CreateView):
    '''
    Page for moving inventory between warehouses.
    Currently only supports products.
    '''
    template_name = os.path.join('inventory', 'transfer', 'create.html')
    form_class = forms.TransferOrderForm
    success_url = reverse_lazy('inventory:home')

    def get_initial(self):
        return {
            'source_warehouse': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        resp = super(TransferOrderCreateView, self).post(
            request, *args, **kwargs)
        if not self.object:
            return resp 
        
        data = json.loads(urllib.parse.unquote(request.POST['items'])) 
        for i in data:
            pk, _ = i['item'].split('-')[0]
            product = models.Product.objects.get(pk=pk)
            wh_item = self.object.source_warehouse.get_item(product)
            if wh_item and wh_item.quantity >= float(i['quantity']):
                models.TransferOrderLine.objects.create(
                    product = product,
                    quantity = i['quantity'],
                    transfer_order = self.object
                )
            else:
                messages.info(request, 'The selected source warehouse has insufficient quantity of item %s to make the transfer' % product)
        return resp

class TransferOrderListView(ExtraContext, PaginationMixin, FilterView):
    filterset_class = filters.TransferOrderFilter
    template_name = os.path.join('inventory', 'transfer', 'list.html')
    paginate_by =10
    extra_context = {
        'title': 'List of Transfer Orders',
        
    }
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['warehouse'] = self.kwargs['pk']
        context['new_link'] = '/inventory/create-transfer-order/' + \
            self.kwargs['pk']
        return context

    def get_queryset(self):
        warehouse = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return models.TransferOrder.objects.filter(Q(source_warehouse=warehouse) | Q(receiving_warehouse=warehouse))

    



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
        warehouse = models.Order.objects.get(pk=self.kwargs['pk']).ship_to
        return {
            'order': self.kwargs['pk'],
            'warehouse': warehouse.pk
        }

    def post(self, request, *args, **kwargs):
        resp = super(StockReceiptCreateView, self).post(request, *args, **kwargs)
        data = json.loads(urllib.parse.unquote(request.POST['received-items']))
        for line in data:
            pk = line['orderItem']
            n = line['quantity']
            if line['medium'] != "":
                medium, _ = line['medium'].split('-')
                models.OrderItem.objects.get(pk=pk).receive(n, medium)
            else:
                models.OrderItem.objects.get(pk=pk).receive(n)
            
        #make transaction after receiving each item.
        #self.object.create_entry()
        return resp 

class GoodsReceivedVoucherView(InventoryControllerCheckMixin, ConfigMixin, 
        DetailView):
    model = models.StockReceipt
    template_name = os.path.join("inventory", "goods_received", "voucher.html")

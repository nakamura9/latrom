# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework.viewsets import ModelViewSet
from django_filters.views import FilterView
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

import forms
import models
import serializers
import filters
from common_data.utilities import ExtraContext,load_config, apply_style, Modal


class InventoryHome(LoginRequiredMixin, ExtraContext, FilterView):
    extra_context = {
        "title": "Inventory Home",
        "new_link": reverse_lazy("inventory:item-create")
        }
    paginate_by = 10
    filterset_class = filters.ItemFilter
    template_name = os.path.join("inventory", "inventory_list.html")

    def get_queryset(self):
        return models.Item.objects.all().order_by('pk')
        
################################################
#              Item views                      #
################################################

class ItemAPIView(ModelViewSet):
    queryset = models.Item.objects.all()
    serializer_class = serializers.ItemSerializer

class ItemDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.Item
    success_url = reverse_lazy('inventory:item-list')

class ItemUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    form_class = forms.ItemUpdateForm
    model = models.Item
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "create_template.html")
    extra_context = {"title": "Update Existing Item"}

class ItemDetailView(LoginRequiredMixin, DetailView):
    model = models.Item
    template_name = os.path.join("inventory", "item_detail.html")


class ItemListView(LoginRequiredMixin, ExtraContext, FilterView):
    paginate_by = 10
    filterset_class = filters.ItemFilter
    template_name = os.path.join('inventory', 'item_list.html')
    extra_context = {
        'title': 'Item List',
        "new_link": reverse_lazy("inventory:item-create")
    }

    def get_queryset(self):
        return models.Item.objects.all().order_by('pk')


class ItemCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    form_class = forms.ItemForm
    model = models.Item
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")
    extra_context = {
        "title": "Create New Item",
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

class QuickItemCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    form_class = forms.QuickItemForm
    model = models.Item
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "crispy_create_template.html")

################################################
#              Order views                     #
################################################

class OrderAPIView(ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer

class OrderCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    '''The front end page combines with react to create a dynamic
    table for entering items in the form.
    The two systems communicate of json encoded strings 
    passed as hidden input fields on the form as part of a
    list of 'items[]'. '''
    form_class = forms.OrderForm
    model = models.Order
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("inventory", "order_create.html")
    extra_context = {
        "title": "Create New Purchase Order",
        "modals": [
        Modal(**{
            'title': 'Add Supplier',
            'action': reverse_lazy('inventory:supplier-create'),
            'form': forms.SupplierForm
        }),
        Modal(**{
            'title': 'Quick Item',
            'action': reverse_lazy('inventory:item-create'),
            'form': forms.QuickItemForm
        })]}

    def post(self, request, *args, **kwargs):
        resp = super(OrderCreateView, self).post(request, *args, **kwargs)
        items = request.POST.getlist("items[]")
        order = models.Order.objects.latest('pk')
        
        for item in items:
            data = json.loads(urllib.unquote(item))
            order.orderitem_set.create(
                item=models.Item.objects.get(
                    pk=data['item_name']),
                    quantity=data['quantity'],
                    order_price=data['order_price'])   
        
        #create transaction after loading all the items
        if order.type_of_order == 0:#cash
            order.create_immediate_entry()
        elif order.type_of_order == 1:
            order.create_deffered_entry()

        return resp
        
class OrderUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    form_class = forms.OrderForm
    model = models.Order
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("inventory", "order_update.html")
    extra_context = {"title": "Update Existing Purchase Order"}

    def post(self, request, *args, **kwargs):
        resp = super(OrderUpdateView, self).post(request, *args, **kwargs)
        items = request.POST.getlist("items[]")
        order = self.get_object()

        for item in items:
            data = json.loads(urllib.unquote(item))
            order.orderitem_set.create(
                item=models.Item.objects.get(
                    pk=data['item_name']),
                    quantity=data['quantity'],
                    order_price=data['order_price'])

        for pk in request.POST.getlist("removed_items[]"):
            models.OrderItem.objects.get(pk=pk).delete()

        #create adjustment transaction if the amount changes
        return resp


class OrderListView(LoginRequiredMixin, ExtraContext, FilterView):
    paginate_by = 10
    filterset_class = filters.OrderFilter
    template_name = os.path.join("inventory", "order_list.html")
    extra_context = {"title": "Order List",
                    "new_link": reverse_lazy("inventory:order-create")}

    def get_queryset(self):
        return models.Order.objects.all().order_by('pk')

class OrderStatusView(LoginRequiredMixin, ExtraContext, DetailView):
    template_name = os.path.join('inventory', 'order_status.html')
    model = models.Order

class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Order
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('inventory:order-list')


class OrderDetailView(LoginRequiredMixin, ExtraContext, DetailView):
    model = models.Order
    template_name = os.path.join('inventory', 'order_templates', 'order.html')
    extra_context = {
        'title': 'Purchase Order',
    }

    def get_context_data(self, *args, **kwargs):
        context = super(OrderDetailView, self).get_context_data(*args, **kwargs)
        context.update(load_config())
        return apply_style(context)

################################################
#              Supplier views                  #
################################################

class SupplierCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    form_class = forms.SupplierForm
    model = models.Supplier
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "create_template.html")
    extra_context = {"title": "Create New Supplier"}

class SupplierUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    form_class = forms.SupplierForm
    model = models.Supplier
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "create_template.html")
    extra_context = {"title": "Update Existing Supplier"}

class SupplierListView(LoginRequiredMixin, ExtraContext, FilterView):
    paginate_by = 10
    filterset_class = filters.SupplierFilter
    template_name = os.path.join("inventory", "supplier_list.html")
    extra_context = {"title": "Supplier List",
                    "new_link": reverse_lazy("inventory:supplier-create")}

    def get_queryset(self):
        return models.Supplier.objects.all().order_by('pk')
                    
class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url=reverse_lazy('inventory:supplier-list')
    model = models.Supplier

################################################
#                  Misc views                  #
################################################

class UnitCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.UnitForm
    model = models.UnitOfMeasure
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join('common_data', 'create_template.html')
    
class OrderItemAPIView(ModelViewSet):
    queryset = models.OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer    

class StockReceiptCreateView(LoginRequiredMixin,CreateView):
    form_class = forms.StockReceiptForm
    model = models.StockReceipt
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("inventory", "stock_receipt.html")
    extra_context = {"title": "Receive Ordered goods"}

    def post(self, request, *args, **kwargs):
        resp = super(StockReceiptCreateView, self).post(request, *args, **kwargs)
        data = json.loads(urllib.unquote(request.POST['received-items']))
        for key in data.keys():
            _ , pk = key.split('-')
            models.OrderItem.objects.get(pk=pk).receive(data[key])
            
        #make transaction after receiving each item.
        self.object.create_entry()
        return resp 

class GoodsReceivedVoucherView(LoginRequiredMixin, DetailView):
    model = models.StockReceipt
    template_name = os.path.join("inventory", "goods_received.html")

    def get_context_data(self, *args, **kwargs):
        context = super(GoodsReceivedVoucherView, self).get_context_data(*args, **kwargs)
        context.update(load_config())
        return apply_style(context)

class CategoryCreateView(LoginRequiredMixin, CreateView):
    form_class = forms.CategoryForm
    model = models.Category
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("common_data", "create_template.html")
    extra_context = {"title": "Category"}

class UnitDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.UnitOfMeasure
    success_url = reverse_lazy('invoicing.item-list')

class ConfigView(LoginRequiredMixin, FormView):
    template_name = os.path.join('inventory', 'config.html')
    form_class = forms.ConfigForm
    success_url = reverse_lazy('inventory:home')
    
    def get_initial(self):
        return load_config()

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            config = load_config()
            new_config = dict(config)
            new_config.update(request.POST.dict())
            json.dump(new_config, open('config.json', 'w'))
        return super(ConfigView, self).post(request)

@login_required
def create_stock_receipt_from_order(request, pk):
    order = get_object_or_404(models.Order, pk=pk)
    order.receive()
    return HttpResponseRedirect(reverse_lazy('inventory:home'))
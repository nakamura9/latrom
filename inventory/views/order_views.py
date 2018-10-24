# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from wkhtmltopdf import utils as pdf_tools
from wkhtmltopdf.views import PDFTemplateView

from common_data.forms import SendMailForm
from common_data.models import GlobalConfig
from common_data.utilities import *
from common_data.views import PaginationMixin, EmailPlusPDFMixin
from inventory import filters, forms, models, serializers
from invoicing.models import SalesConfig

from .common import CREATE_TEMPLATE, InventoryControllerCheckMixin


class OrderAPIView(ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer


class OrderPOSTMixin(object):
    def post(self, request, *args, **kwargs):
        update_flag = isinstance(self, UpdateView)
        resp = super(OrderPOSTMixin, self).post(request, *args, **kwargs)
        items = json.loads(urllib.parse.unquote(request.POST["items"]))
        if not self.object:
           return resp

        order = self.object
        if update_flag:
            for i in self.object.orderitem_set.all():
                i.delete()

        for data in items:
            item_type = data['pk'][0]
            pk = data['pk'].strip(item_type)
            if item_type == 'P':
                product = models.Product.objects.get(pk=pk)
                order.orderitem_set.create(
                    product=product,
                    item_type=1,
                    quantity=data['quantity'],
                    order_price=data['order_price'])
            elif item_type == 'E':
                equipment = models.Equipment.objects.get(pk=pk)
                order.orderitem_set.create(
                    equipment=equipment,
                    item_type=3,
                    quantity=data['quantity'],
                    order_price=data['order_price'])
            elif item_type == 'C':
                consumable = models.Consumable.objects.get(pk=pk)
                order.orderitem_set.create(
                    consumable=consumable,
                    item_type=2,
                    quantity=data['quantity'],
                    order_price=data['order_price'])   
        
        #create transaction after loading all the items
        #vary based on order status
        
        if not update_flag: 
            order.create_entry()

        return resp        

class OrderCreateView(InventoryControllerCheckMixin, ExtraContext, OrderPOSTMixin, CreateView):
    '''The front end page combines with react to create a dynamic
    table for entering items in the form.
    The two systems communicate of json encoded strings 
    passed as hidden input fields on the form as part of a
    list of 'items[]'. '''
    form_class = forms.OrderForm
    model = models.Order
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("inventory", "order", "create.html")
    extra_context = {
        "title": "Create New Purchase Order",
        "modals": [
        Modal(**{
            'title': 'Add Supplier',
            'action': reverse_lazy('inventory:supplier-create'),
            'form': forms.SupplierForm
        }),
        Modal(**{
            'title': 'Quick Product',
            'action': reverse_lazy('inventory:product-create'),
            'form': forms.QuickProductForm
        })]}

    


class OrderUpdateView(InventoryControllerCheckMixin, ExtraContext, 
        OrderPOSTMixin,UpdateView):
    form_class = forms.OrderForm
    model = models.Order
    success_url = reverse_lazy('inventory:home')
    template_name = os.path.join("inventory", "order", "update.html")
    extra_context = {"title": "Update Existing Purchase Order"}


class OrderListView(InventoryControllerCheckMixin, ExtraContext, PaginationMixin, FilterView):
    paginate_by = 10
    filterset_class = filters.OrderFilter
    template_name = os.path.join("inventory", "order", "list.html")
    extra_context = {"title": "Order List",
                    "new_link": reverse_lazy("inventory:order-create")}

    def get_queryset(self):
        return models.Order.objects.all().order_by('pk')


class OrderStatusView(InventoryControllerCheckMixin, ExtraContext, DetailView):
    template_name = os.path.join('inventory', 'order', 'status.html')
    model = models.Order


class OrderDeleteView(InventoryControllerCheckMixin, DeleteView):
    model = models.Order
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('inventory:order-list')


class OrderDetailView(InventoryControllerCheckMixin, ExtraContext, 
        ConfigMixin, DetailView):
    model = models.Order
    template_name = os.path.join('inventory', 'order', 'detail.html')
    extra_context = {
        'title': 'Purchase Order',
    }


class OrderItemAPIView(ModelViewSet):
    queryset = models.OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer    


#pdf and email
class OrderPDFView(ConfigMixin, PDFTemplateView):
    template_name = os.path.join("inventory", "order",
        'pdf.html')
    file_name = 'order.pdf'
    def get_context_data(self, *args, **kwargs):
        context = super(OrderPDFView, self).get_context_data(*args, **kwargs)
        context['object'] = models.Order.objects.get(pk=self.kwargs['pk'])
        return context

class OrderEmailSendView(EmailPlusPDFMixin):
    inv_class = models.Order
    pdf_template_name = os.path.join("inventory", "order",
            'pdf.html')
    success_url = reverse_lazy('inventory:order-list')
    extra_context = {
        'title': 'Send Purchase Order as PDF attatchment'
    }

    def get_initial(self):
        ord = models.Order.objects.get(pk=self.kwargs['pk'])
        return {
            'recepient': ord.supplier.email
        }
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

from wkhtmltopdf.views import PDFTemplateView
from wkhtmltopdf import utils as pdf_tools
from common_data.forms import SendMailForm
from common_data.models import GlobalConfig 

from django.core.mail import EmailMessage

from common import CREATE_TEMPLATE, InventoryControllerCheckMixin


class OrderAPIView(ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer


class OrderPOSTMixin(object):
    def post(self, request, *args, **kwargs):
        update_flag = self.get_object()
        resp = super(OrderPOSTMixin, self).post(request, *args, **kwargs)
        items = json.loads(urllib.unquote(request.POST["items"]))
        if not self.object:
           return resp

        order = self.object
        if update_flag:
            for i in self.object.orderitem_set.all():
                i.delete()

        for data in items:
            order.orderitem_set.create(
                product=models.Product.objects.get(
                    pk=data['pk']),
                    quantity=data['quantity'],
                    order_price=data['order_price'])   
        
        #create transaction after loading all the items
        #vary based on order status
        
        if not update_flag: 
            if order.type_of_order == 0:#cash
                order.create_immediate_entry()
            elif order.type_of_order == 1:
                order.create_deffered_entry()

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


class OrderListView(InventoryControllerCheckMixin, ExtraContext, FilterView):
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

class OrderEmailSendView(ExtraContext, FormView):
    form_class = SendMailForm
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy('inventory:order-list')
    extra_context = {
        'title': 'Send Purchase Order as PDF attatchment'
    }

    def get_initial(self):
        ord = models.Order.objects.get(pk=self.kwargs['pk'])
        
        return {
            'recepient': ord.supplier.supplier_email
        }
    def post(self,request, *args, **kwargs):
        resp = super(OrderEmailSendView, self).post(
            request, *args, **kwargs)
        form = self.form_class(request.POST)
        
        if not form.is_valid():
            return resp
        
        config = GlobalConfig.objects.get(pk=1)
        msg = EmailMessage(
            subject=form.cleaned_data['subject'],
            body = form.cleaned_data['content'],
            from_email=config.email_user,
            to=[form.cleaned_data['recepient']]
        )
        #create pdf from the command line
        template = os.path.join("inventory", "order",
            'pdf.html')
        out_file = os.path.join(os.getcwd(), 'media', 'temp','out.pdf')
    
        context = {
            'object': models.Order.objects.get(pk=self.kwargs['pk'])
        }
        context.update(SalesConfig.objects.first().__dict__)
        options = {
            'output': out_file
        }
        try:
            pdf_tools.render_pdf_from_template(
                template, None, None, 
                apply_style(context),
                cmd_options=options)
        except:
            raise Exception('Error occured creating pdf')

        if os.path.isfile(out_file):
            msg.attach_file(out_file)
            msg.send()
            os.remove(out_file)

        # if the message is successful delete it.
        return resp
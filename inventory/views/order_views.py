# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.mail import EmailMessage
from django.contrib import messages
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
from common_data.views import PaginationMixin, EmailPlusPDFView, PDFDetailView
from inventory import filters, forms, models, serializers
from invoicing.models import SalesConfig
from accounting.models import Expense, JournalEntry, Account, Journal

from .common import CREATE_TEMPLATE



class OrderAPIView(ModelViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer


class OrderPOSTMixin(object):
    def post(self, request, *args, **kwargs):
        update_flag = isinstance(self, UpdateView)
        try:
            items = json.loads(urllib.parse.unquote(request.POST["items"]))
        except json.JSONDecodeError:
            messages.info(request, 'Please populate the form with the lines of inventory to be ordered.')
            if update_flag:
                return HttpResponseRedirect(
                    '/inventory/order-update/{}'.format(self.object.pk))
            return HttpResponseRedirect('/inventory/order-create')

        resp = super().post(request, *args, **kwargs)

        if not self.object:
           return resp

        order = self.object
        if update_flag:
            for i in self.object.orderitem_set.all():
                i.delete()

        for data in items:
            id= data['item'].split('-')[0] 
            pk = id
            
            unit_id = 1 # default value
            if data['unit'] != "":
                unit_id = data['unit'].split('-')[0]
            
            unit = models.UnitOfMeasure.objects.get(
                        pk=unit_id)
            item = models.InventoryItem.objects.get(pk=pk)
            order.orderitem_set.create(
                item=item,
                quantity=data['quantity'],
                unit=unit,
                order_price=data['order_price'])
            
        #create transaction after loading all the items
        #vary based on order status
        
        order.create_entry()
        if not update_flag:
            if self.request.POST.get('make_payment', None):
                pmt = models.OrderPayment.objects.create(
                    order=order,
                    date=datetime.date.today(),
                    amount=order.total,
                    comments="Autogenerated payment for order %d" % order.pk
                )
                pmt.create_entry()
        return resp        

class OrderCreateView( ContextMixin, 
        OrderPOSTMixin, CreateView):
    '''The front end page combines with react to create a dynamic
    table for entering items in the form.
    The two systems communicate of json encoded strings 
    passed as hidden input fields on the form as part of a
    list of 'items[]'. '''
    form_class = forms.OrderForm
    model = models.Order
    template_name = os.path.join("inventory", "order", "create.html")
    extra_context = {
        "title": "Create Purchase Order",
        "description": "Use this form to order inventory from suppliers. Afterwards inventory may be added to stock using the receive inventory form.",
        "related_links": [
            {
                'name': 'Add Vendor',
                'url': '/inventory/supplier/create'
            },{
                'name': 'Add Product',
                'url': '/inventory/product-create/'
            },{
                'name': 'Add Equipment',
                'url': '/inventory/equipment-create/'
            },{
                'name': 'Add Consumable',
                'url': '/inventory/consumable-create/'
            },

        ],
        'box_array': urllib.parse.quote(json.dumps(
            [{
                'model': 'supplier',
                'app': 'inventory',
                'id': 'id_supplier'
            }
            ]))
        }

    def get_initial(self):
        if self.kwargs.get('supplier', None):
            return {
                'supplier': self.kwargs['supplier']
            }
    


class OrderUpdateView( ContextMixin, 
        OrderPOSTMixin,UpdateView):
    form_class = forms.OrderUpdateForm
    model = models.Order
    template_name = os.path.join("inventory", "order", "update.html")
    extra_context = {"title": "Update Existing Purchase Order"}


class OrderListView( ContextMixin, 
        PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.OrderFilter
    template_name = os.path.join("inventory", "order", "list.html")
    extra_context = {"title": "Purchase Order List",
                    "new_link": reverse_lazy("inventory:order-create")}

    def get_queryset(self):
        return models.Order.objects.all().order_by('pk').reverse()


class OrderStatusView( ContextMixin, DetailView):
    template_name = os.path.join('inventory', 'order', 'status.html')
    model = models.Order


class OrderDeleteView( DeleteView):
    model = models.Order
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('inventory:order-list')


class OrderDetailView( ContextMixin, 
        ConfigMixin, MultiPageDocument, DetailView):
    model = models.Order
    template_name = os.path.join('inventory', 'order', 'detail.html')
    extra_context = {
        'title': 'Purchase Order',
    }
    page_length=20
    
    def get_multipage_queryset(self):
        self.get_object()
        return models.OrderItem.objects.filter(order=self.object)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['pdf_link'] =True
        if self.object.status == "draft":
            context['actions'] = [
                {
                        'name': 'Verify Order',
                        'url': '/inventory/order/{}/verify'.format(
                            self.object.pk)
                    },
            ]
            context['title'] = "Purchase Order(Draft)"
        return context


class OrderPaymentDetailView(  
        ConfigMixin, DetailView):
    model = models.Order
    template_name = os.path.join('inventory', 'order', 'payment_list.html')
   


class OrderPaymentCreateView( ContextMixin,
        ConfigMixin, CreateView):
    model = models.OrderPayment
    template_name= CREATE_TEMPLATE
    success_url = "/inventory/"
    form_class = forms.OrderPaymentForm
    extra_context = {
        'title': 'Make payment on order'
    }

    def get_initial(self):
        return {
            'order': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)

        if self.object:
            self.object.create_entry()

        return resp

class OrderItemAPIView(ModelViewSet):
    queryset = models.OrderItem.objects.all()
    serializer_class = serializers.OrderItemSerializer    


#pdf and email
class OrderPDFView(ConfigMixin, MultiPageDocument, PDFTemplateView):
    template_name = os.path.join("inventory", "order",
        'pdf.html')
    file_name = 'order.pdf'
    page_length=20

    def get_multipage_queryset(self):
        obj = models.Order.objects.get(pk=self.kwargs['pk'])
        return models.OrderItem.objects.filter(order=obj)

    def get_context_data(self, *args, **kwargs):
        context = super(OrderPDFView, self).get_context_data(*args, **kwargs)
        context['object'] = models.Order.objects.get(pk=self.kwargs['pk'])
        return context

class OrderEmailSendView(ConfigMixin, EmailPlusPDFView):
    inv_class = models.Order
    pdf_template_name = os.path.join("inventory", "order",
            'pdf.html')
    success_url = reverse_lazy('inventory:order-list')
    

class ShippingCostDetailView(DetailView):
    # TODO test
    template_name = os.path.join("inventory", "order", "shipping_list.html")
    model = models.Order


class ShippingAndHandlingView( 
        ContextMixin, FormView):
    template_name = CREATE_TEMPLATE
    form_class = forms.ShippingAndHandlingForm
    success_url = reverse_lazy("inventory:order-list")
    extra_context = {
        'title': 'Record Shipping and handling'
    }

    def get_initial(self):
        return {
            'reference': 'ORD{}'.format(self.kwargs['pk'])
        }
    
    def form_valid(self, form):
        resp =  super().form_valid(form)
        entry = JournalEntry.objects.create(
            date=form.cleaned_data['date'], 
            memo=form.cleaned_data['description'], 
            journal=Journal.objects.get(pk=2),#disbursements
            created_by=form.cleaned_data['recorded_by'],
            draft=False
        )
        # the unit cost changes but the journal entry for the cost 
        # of the order remains the same
        entry.simple_entry(
            form.cleaned_data['amount'],
            Account.objects.get(pk=1000),
            Account.objects.get(pk=4009)
            )
        
        order = models.Order.objects.get(pk=self.kwargs['pk'])
        order.shipping_cost_entries.add(entry)
        order.save()


        return resp

    
def verify_order(request, pk=None):
    order = get_object_or_404(models.Order, pk=pk)
    order.status = "order"
    order.save()
    return HttpResponseRedirect('/inventory/order-detail/{}'.format(order.pk))

class DebitNoteCreateView(CreateView):
    form_class = forms.DebitNoteForm
    template_name = os.path.join("inventory", "order", "debit_note", "create.html")
    model = models.DebitNote

    def get_initial(self):
        return {
            'order': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        resp =  super().post(request, *args, **kwargs)

        if not self.object:
            return resp

        data = json.loads(urllib.parse.unquote(request.POST['returned-items']))

        for line in data:
            pk = line['item'].split('-')[0]
            item = models.OrderItem.objects.get(pk=pk)
            if float(line['quantity']) > 0:
                models.DebitNoteLine.objects.create(
                    note=self.object,
                    item=item,
                    quantity=float(line['quantity'])
                )
                # TODO test
                item._return_to_vendor(float(line['quantity']))
                
        return resp

class DebitNoteListView(DetailView):
    template_name = os.path.join("inventory", "order", "debit_note", "list.html")
    model = models.Order

class DebitNoteDetailView(ContextMixin, 
                            ConfigMixin, 
                            MultiPageDocument, 
                            DetailView):
    template_name = os.path.join("inventory", "order", "debit_note", 
        "detail.html")
    model = models.DebitNote
    extra_context = {
        'title': 'Debit Note',
        'pdf_link': True
    }
    page_length =16

    def get_multipage_queryset(self):
        return models.DebitNoteLine.objects.filter(
            note=models.DebitNote.objects.get(
                pk=self.kwargs['pk']))


class DebitNotePDFView(ConfigMixin, MultiPageDocument, PDFDetailView):
    template_name = os.path.join("inventory", "order", "debit_note", 
        "detail.html")
    model = models.DebitNote
    context = {
        'title': 'Debit Note'
    }
    page_length =16

    def get_multipage_queryset(self):
        return models.DebitNoteLine.objects.filter(
            note=models.DebitNote.objects.get(
                pk=self.kwargs['pk']))
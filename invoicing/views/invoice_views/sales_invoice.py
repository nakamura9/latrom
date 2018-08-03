# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from rest_framework import viewsets

from invoicing import forms
from common_data.utilities import ExtraContext, apply_style
from inventory.models import Item
from invoicing.models import *
from invoicing import filters
from invoicing import serializers
from invoicing.views.common import  SalesRepCheckMixin



class SalesInvoiceListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "Sales Invoice List",
                    "new_link": reverse_lazy("invoicing:create-sales-invoice")}
    template_name = os.path.join("invoicing", "sales_invoice","list.html")
    filterset_class = filters.AbstractInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return SalesInvoice.objects.filter(active=True).order_by('date')
    

class SalesInvoiceDetailView(SalesRepCheckMixin, DetailView):
    model = SalesInvoice
    template_name = os.path.join("invoicing", "sales_invoice",
        'detail.html')
    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoiceDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        context['title'] = context.get('invoice_title', "Invoice")
        return apply_style(context)

        
class SalesInvoiceCreateView(SalesRepCheckMixin, ExtraContext, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    extra_context = {
        "title": "Create a New Invoice"
        }
            
    template_name = os.path.join("invoicing","sales_invoice", "create.html")
    form_class = forms.SalesInvoiceForm
    success_url = reverse_lazy("invoicing:home")
    model = SalesInvoice

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoiceCreateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(SalesInvoiceCreateView, self).post(request, *args, **kwargs)
        if not self.object:
            return resp

        inv = self.object
        
        items = request.POST.get("item_list", None)
        if items:
            items = json.loads(urllib.unquote(items))
            print items
            for item in items:

                pk, name = item['item_name'].split('-')
                inv.add_item(Item.objects.get(pk=pk), 
                    item['quantity'])
        
        # moved here because the invoice item data must first be 
        # saved in the database before inventory and entries 
        # can be created
        if inv.status in ['draft', 'quotation']:
            pass
        elif inv.status == 'sent': 
            inv.update_inventory()
            inv.create_credit_entry()
        elif inv.status == 'paid':
            inv.update_inventory()
            inv.create_cash_entry()
        else:
            pass

        return resp


class SalesDraftUpdateView(UpdateView):
    model = SalesInvoice
    form_class = forms.SalesInvoiceForm
    template_name = os.path.join('invoicing', 'sales_invoice','create.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')

    def get_context_data(self, *args, **kwargs):
        context = super(SalesDraftUpdateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(SalesDraftUpdateView, self).post(request, *args, **kwargs)

        #remove existing lines
        for line in self.object.salesinvoiceline_set.all():
            line.delete()
        #create new lines 
        items = request.POST.get("item_list", None)
        if items:
            items = json.loads(urllib.unquote(items))
            for item in items:
                pk, name = item['item_name'].split('-')
                self.object.add_item(Item.objects.get(pk=pk), 
                    item['quantity'])
        
        # moved here because the invoice item data must first be 
        # saved in the database before inventory and entries 
        # can be created
        if self.object.status in ['draft', 'quotation']:
            pass
        elif self.object.status == 'sent': 
            self.object.update_inventory()
            self.object.create_credit_entry()
        elif inv.status == 'paid':
            self.object.update_inventory()
            self.object.create_cash_entry()
        else:
            pass

        return resp


class SalesInvoiceUpdateView(ExtraContext, UpdateView):
    extra_context = {
        'title': 'Edit Sales Invoice Details'
    }
    model = SalesInvoice
    form_class = forms.SalesInvoiceUpdateForm
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')


def apply_full_payment_on_invoice(request):
    pass


class SalesInvoiceAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SalesInvoiceSerializer
    queryset = SalesInvoice.objects.all()

class SalesInvoicePaymentView(ExtraContext, CreateView):
    model = Payment
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.SalesInvoicePaymentForm
    success_url = reverse_lazy('invoicing:sales-invoice-list')
    extra_context= {
        'title': 'Apply Payment to Sales Invoice'
    }

    def get_initial(self):
        return {
            'sales_invoice': self.kwargs['pk'],
            'payment_for': 0
            }

class SalesInvoicePaymentDetailView(ListView):
    template_name = os.path.join('invoicing', 'sales_invoice', 
        'payment', 'detail.html')

    def get_queryset(self):
        return Payment.objects.filter(sales_invoice=SalesInvoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoicePaymentDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        return context
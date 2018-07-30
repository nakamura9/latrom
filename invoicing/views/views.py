# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from rest_framework import generics, viewsets
from django_filters.views import FilterView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.conf import settings
from invoicing import forms

from common_data.utilities import ExtraContext, apply_style, Modal
from inventory.forms import QuickItemForm
from accounting.forms import TaxForm
from inventory.models import Item
from invoicing.models import *
from invoicing import filters
from invoicing import serializers


class SalesRepCheckMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif hasattr(self.request.user, 'employee') and \
                self.request.user.employee.is_sales_rep:
            return True
        else:
            return False

class Home(SalesRepCheckMixin, TemplateView):
    template_name = os.path.join("invoicing", "home.html")

        

#########################################
#               Invoice Views           #
#########################################

class InvoiceAPIViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.filter(active=True)
    serializer_class = serializers.InvoiceSerializer

class InvoiceItemAPIViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = serializers.InvoiceItemSerializer


class InvoiceDeleteView(SalesRepCheckMixin, DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = Invoice
    success_url = reverse_lazy("invoicing:invoices-list")

class InvoiceListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "Invoice List",
                    "new_link": reverse_lazy("invoicing:create-invoice")}
    template_name = os.path.join("invoicing", "invoice_list.html")
    filterset_class = filters.InvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(active=True).order_by('date_issued')
    

class InvoiceDetailView(SalesRepCheckMixin, DetailView):
    model = Invoice
    template_name = os.path.join("invoicing", "invoice_templates",
        'invoice.html')
    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        context['title'] = context.get('invoice_title', "Invoice")
        return apply_style(context)

        
class InvoiceCreateView(SalesRepCheckMixin, ExtraContext, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    extra_context = {
        "title": "Create a New Invoice",
        'modals': [
            Modal('Quick Tax', 
                '/accounting/api/tax/',
                TaxForm),
            Modal('Quick Customer',
                reverse_lazy('invoicing:quick-customer'),
                forms.QuickCustomerForm),
            Modal('Quick Item',
                reverse_lazy('inventory:quick-item'),
                QuickItemForm),
        ]
        }
            
    template_name = os.path.join("invoicing", "invoice_create.html")
    form_class = forms.InvoiceForm
    success_url = reverse_lazy("invoicing:home")

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceCreateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    

    def post(self, request, *args, **kwargs):
        resp = super(InvoiceCreateView, self).post(request, *args, **kwargs)
        inv = Invoice.objects.latest("pk")
        for item in request.POST.getlist("items[]"):
            data = json.loads(urllib.unquote(item))
            inv.add_item(Item.objects.get(pk=data['code']), 
                data['quantity'], data['discount'])
        
        # moved here because the invoice item data must first be 
        # saved in the database before inventory and entries 
        # can be created
        inv.create_entry()
        inv.update_inventory()

        return resp

class InvoiceUpdateView(SalesRepCheckMixin, ExtraContext, UpdateView):
    '''An update view is similar to a create view but it allows the 
    user to remove existing items from a quote using the list 
    of hidden inputs called 'removed_items[]'. '''

    extra_content = {"title": "Update Invoice"}
    template_name = os.path.join("invoicing", "invoice_update.html")
    model = Invoice
    form_class = forms.InvoiceUpdateForm
    success_url = reverse_lazy("invoicing:home")

    def post(self, request, *args, **kwargs):
        # implement check for whether an entry exists
        resp = super(InvoiceUpdateView, self).post(request, *args, **kwargs)
        inv = self.get_object()
        for item in request.POST.getlist("items[]"):
            data = json.loads(urllib.unquote(item))
            inv.add_item(Item.objects.get(pk=data['code']), 
                data['quantity'],data['discount'])
        for pk in request.POST.getlist("removed_items[]"):
            InvoiceItem.objects.get(pk=pk).delete()
        
        return resp

#########################################
#                 Quote Views           #
#########################################

class QuoteAPIViewSet(viewsets.ModelViewSet):
    queryset = Quote.objects.all()
    serializer_class = serializers.QuoteSerializer

class QuoteItemAPIViewSet(viewsets.ModelViewSet):
    queryset = QuoteItem.objects.all()
    serializer_class = serializers.QuoteItemSerializer

class QuoteCreateView(SalesRepCheckMixin, ExtraContext, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    extra_context = {
        "title": "Create a New Quotation",
        'modals': [
            Modal('Quick Tax', 
                '/accounting/api/tax/',
                TaxForm),
            Modal('Quick Customer',
                reverse_lazy('invoicing:quick-customer'),
                forms.QuickCustomerForm),
            Modal('Quick Item',
                reverse_lazy('inventory:quick-item'),
                QuickItemForm),
        ]}
    template_name = os.path.join("invoicing", "quote_create.html")
    model = Quote
    form_class = forms.QuoteForm
    success_url = reverse_lazy("invoicing:home")

    def get_context_data(self, *args, **kwargs):
        context = super(QuoteCreateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(QuoteCreateView, self).post(request, *args, **kwargs)
        quo = Quote.objects.latest("pk")
        for item in request.POST.getlist("items[]"):
            data = json.loads(urllib.unquote(item))
            quo.add_item(Item.objects.get(pk=data['code']),
                data['quantity'], data['discount'])
        
        return resp


class QuoteUpdateView(SalesRepCheckMixin, ExtraContext, UpdateView):
    '''An update view is similar to a create view but it allows the 
    user to remove existing items from a quote using the list 
    of hidden inputs called 'removed_items[]'. '''
    
    extra_content = {"title": "Update an existing Quotation"}
    template_name = os.path.join("invoicing", "quote_update.html")
    model = Quote
    form_class = forms.QuoteForm
    success_url = reverse_lazy("invoicing:home")

    def post(self, request, *args, **kwargs):
        resp = super(QuoteUpdateView, self).post(request, *args, **kwargs)
        quo = Quote.objects.latest("pk")
        # add update prices toggle for for each quote item item
        for item in request.POST.getlist("items[]"):
            data = json.loads(urllib.unquote(item))
            quo.quoteitem_set.create(
                quantity=data['quantity'],
                item=Item.objects.get(pk=data['code']),
                discount=data['discount'])

        for pk in request.POST.getlist("removed_items[]"):
            QuoteItem.objects.get(pk=pk).delete()
        
        return resp

class QuoteDetailView(SalesRepCheckMixin, DetailView):
    model = Quote
    template_name = os.path.join("invoicing", "quote_templates",
        'quote.html')
    
    def get_context_data(self, *args, **kwargs):
        context = super(QuoteDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        context['title'] = 'Quotation'
        return apply_style(context)


class QuoteListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {
        "title": "Quotation List",
        "new_link": reverse_lazy("invoicing:create-quote")
        }
    template_name = os.path.join("invoicing", "quote_list.html")
    filterset_class = filters.QuoteFilter
    paginate_by = 10

    def get_queryset(self):
        return Quote.objects.all().order_by('date')
    
class QuoteDeleteView(SalesRepCheckMixin, DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = Quote
    success_url = reverse_lazy("invoicing:quote-list")


#########################################
#               Receipt Views           #
#########################################

class ReceiptDetailView(SalesRepCheckMixin, DetailView):
    model = Payment
    template_name = os.path.join("invoicing", "receipt_templates",
        'receipt.html')
    
    def get_context_data(self, *args, **kwargs):
        context = super(ReceiptDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        context['title'] = 'Receipt'
        return apply_style(context)


class InvoiceReceiptDetailView(SalesRepCheckMixin, DetailView):
    model = Invoice
    template_name = os.path.join("invoicing", "receipt_templates",
        'invoice_receipt.html')
    
    def get_context_data(self, *args, **kwargs):
        context = super(InvoiceReceiptDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        context['title'] = 'Receipt'
        return apply_style(context)



#########################################################
#                  Template Views                       #
#########################################################


class ConfigView(SalesRepCheckMixin, UpdateView):
    template_name = os.path.join("invoicing", "config.html")
    form_class = forms.SalesConfigForm
    model = SalesConfig
    success_url = reverse_lazy('invoicing:home')
    
    
class ConfigAPIView(generics.RetrieveAPIView):
    queryset = SalesConfig.objects.all()
    serializer_class = serializers.ConfigSerializer

@login_required
def create_payment_from_invoice(request, pk=None):
    invoice = get_object_or_404(Invoice, pk=pk)
    invoice.create_payment()
    return HttpResponseRedirect(reverse('invoicing:home'))


@login_required
def create_invoice_from_quote(request, pk=None):
    quote = get_object_or_404(Quote, pk=pk)
    quote.create_invoice()
    return HttpResponseRedirect(reverse('invoicing:home'))
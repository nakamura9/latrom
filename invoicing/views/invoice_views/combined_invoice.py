# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django_filters.views import FilterView
from django.urls import reverse_lazy
from invoicing import forms

from common_data.utilities import ExtraContext, apply_style
from inventory.models import Item
from invoicing.models import *
from invoicing import filters
from invoicing import serializers
from invoicing.views.common import  SalesRepCheckMixin


class CombinedInvoiceListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "Combined Invoice List",
                    "new_link": reverse_lazy("invoicing:create-combined-invoice")}
    template_name = os.path.join("invoicing", "combined_invoice","list.html")
    filterset_class = filters.AbstractInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return CombinedInvoice.objects.filter(active=True).order_by('date')
    

class CombinedInvoiceDetailView(SalesRepCheckMixin, DetailView):
    model = CombinedInvoice
    template_name = os.path.join("invoicing", "combined_invoice",
        'detail.html')
    def get_context_data(self, *args, **kwargs):
        context = super(CombinedInvoiceDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        return apply_style(context)

        
class CombinedInvoiceCreateView(SalesRepCheckMixin, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","combined_invoice", "create.html")
    form_class = forms.CombinedInvoiceForm
    success_url = reverse_lazy("invoicing:home")

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    def get_context_data(self, *args, **kwargs):
        context = super(CombinedInvoiceCreateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(CombinedInvoiceCreateView, self).post(request, *args, **kwargs)
        
        if not self.object:
            return resp
            
        inv = self.object
        items = request.POST.get("item_list", None)
        
        if items:
            items = json.loads(urllib.unquote(items))
            print items
            for item in items:
                inv.add_line(item)
                
        # moved here because the invoice item data must first be 
        # saved in the database before inventory and entries 
        # can be created
        
        if inv.status == 'sent': 
            inv.create_credit_entry()
        elif inv.status == 'paid':
            inv.create_cash_entry()
        else:#includes drafts and quotations
            pass

        return resp
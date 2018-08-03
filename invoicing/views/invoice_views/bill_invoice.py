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
from invoicing.views.common import SalesRepCheckMixin


class BillListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "Customer Bill List",
                    "new_link": reverse_lazy("invoicing:create-bill")}
    template_name = os.path.join("invoicing", "bill","list.html")
    filterset_class = filters.AbstractInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return Bill.objects.filter(active=True).order_by('date')
    

class BillDetailView(SalesRepCheckMixin, DetailView):
    model = Bill
    template_name = os.path.join("invoicing", "bill",
        'detail.html')
    def get_context_data(self, *args, **kwargs):
        context = super(BillDetailView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        return apply_style(context)

        
class BillCreateView(SalesRepCheckMixin, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    
    template_name = os.path.join("invoicing","bill", "create.html")
    form_class = forms.BillForm
    success_url = reverse_lazy("invoicing:home")

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    def get_context_data(self, *args, **kwargs):
        context = super(BillCreateView, self).get_context_data(*args, **kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        apply_style(context)
        return context

    def post(self, request, *args, **kwargs):
        resp = super(BillCreateView, self).post(request, *args, **kwargs)
        inv = Bill.objects.latest("pk")
        data = request.POST.get("item_list", None)
        items = json.loads(urllib.unquote(data))
        for item in items:
            inv.add_line(item['pk'])
        
        # moved here because the invoice item data must first be 
        # saved in the database before inventory and entries 
        # can be created
        if inv.status in ['draft', 'quotation']:
            pass
        elif inv.status == 'sent': 
            inv.create_credit_entry()
        elif inv.status == 'paid':
            inv.create_cash_entry()
        else:
            pass

        return resp
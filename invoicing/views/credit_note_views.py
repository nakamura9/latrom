# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView
from rest_framework import generics, viewsets

from accounting.forms import TaxForm
from common_data.utilities import ConfigMixin, ExtraContext, Modal
from common_data.views import PaginationMixin
from inventory.forms import QuickProductForm
from inventory.models import Product
from invoicing import filters, forms, serializers
from invoicing.models import CreditNote, SalesConfig, SalesInvoiceLine

from .common import SalesRepCheckMixin

#########################################
#           Credit Note Views              #
#########################################

class CreditNoteCreateView(SalesRepCheckMixin, ExtraContext, CreateView):
    '''Credit notes are created along with react on the front end.
    each note tracks each invoice item and returns the quantity 
    of the item that was returned. The data is shared as a single 
    urlencoded json string. this string is an object that maps 
    keys to values where the key is the primary key of the invoice item
    and the value is the quantity returned. Django handles the return on the
    database side of things.
    '''
    extra_context = {"title": "Create New Credit Note"}
    template_name = os.path.join("invoicing", "sales_invoice", 
        "credit_note", "create.html")
    model = CreditNote
    form_class = forms.CreditNoteForm
    success_url = reverse_lazy("invoicing:sales-invoice-list")

    def get_initial(self):
        return {
            'invoice': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        resp = super(CreditNoteCreateView, self).post(request, *args, **kwargs)

        if not self.object:
            return resp

        data = json.loads(urllib.parse.unquote(request.POST['returned-items']))
        for key in data.keys():
            iitem = SalesInvoiceLine.objects.get(pk=key)
            iitem._return(data[key])

        return resp


class CreditNoteUpdateView(SalesRepCheckMixin, ExtraContext, UpdateView):
    extra_context = {"title": "Update Existing Credit Note"}
    template_name = os.path.join("invoicing", "create_credit_note.html")
    model = CreditNote
    form_class = forms.CreditNoteForm
    success_url = reverse_lazy("invoicing:home")


class CreditNoteDetailView(SalesRepCheckMixin, ConfigMixin, DetailView):
    template_name = os.path.join('invoicing', 'sales_invoice', 'credit_note', 'detail.html')
    model = CreditNote
    
    def get_context_data(self, *args, **kwargs):
        context = super(CreditNoteDetailView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Credit Note'
        return context

#Deprecated
#credit notes now accessed on an invoice by invoice basis
class CreditNoteListView(SalesRepCheckMixin, ExtraContext, PaginationMixin, FilterView):
    extra_context = {"title": "List of Credit Notes"}
    template_name = os.path.join("invoicing", "sales_invoice", "credit_note", "list.html")
    filterset_class = filters.CreditNoteFilter
    paginate_by = 10

    def get_queryset(self):
        return CreditNote.objects.all().order_by('date')

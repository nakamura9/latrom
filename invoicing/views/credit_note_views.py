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
from common_data.utilities import ExtraContext, ConfigMixin, Modal
from inventory.forms import QuickProductForm
from accounting.forms import TaxForm
from inventory.models import Product
from invoicing.models import CreditNote, SalesInvoiceLine, SalesConfig
from invoicing import filters
from invoicing import serializers
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
class CreditNoteListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "List of Credit Notes",
                    "new_link": reverse_lazy("invoicing:credit-note-create")}
    template_name = os.path.join("invoicing", "credit_note_list.html")
    filterset_class = filters.CreditNoteFilter
    paginate_by = 10

    def get_queryset(self):
        return CreditNote.objects.all().order_by('date')
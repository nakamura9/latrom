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
from common_data.utilities import ConfigMixin, ContextMixin, MultiPageDocument
from common_data.views import PaginationMixin, PDFDetailView
from invoicing import filters, forms, serializers
from invoicing.models import CreditNote, SalesConfig
from invoicing.models.credit_note import CreditNoteLine
from invoicing.models.invoice import InvoiceLine, Invoice 

#########################################
#           Credit Note Views           #
#########################################

class CreditNoteCreateView( ContextMixin, CreateView):
    '''Credit notes are created along with react on the front end.
    each note tracks each invoice item and returns the quantity 
    of the item that was returned. The data is shared as a single 
    urlencoded json string. this string is an object that maps 
    keys to values where the key is the primary key of the invoice item
    and the value is the quantity returned. Django handles the return on the
    database side of things.
    '''
    extra_context = {"title": "Create New Credit Note"}
    template_name = os.path.join("invoicing", "invoice", 
        "credit_note", "create.html")
    model = CreditNote
    form_class = forms.CreditNoteForm

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'invoice': self.kwargs['pk'],
            'comments': config.default_credit_note_comments
        }

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)

        if not self.object:
            return resp
            

        data = json.loads(urllib.parse.unquote(request.POST['returned-items']))
        
        for line in data:
            pk = line['product'].split('-')[0]
            inv_line = InvoiceLine.objects.get(pk=pk)
            # to ensure duplicate returns are not made
            CreditNoteLine.objects.create(
                line=inv_line,
                note=self.object,
                quantity=float(line["returned_quantity"])
            )
            
            inv_line.product._return(float(line["returned_quantity"]))

        self.object.create_entry()

        return resp


class CreditNoteUpdateView( ContextMixin, UpdateView):
    extra_context = {"title": "Update Existing Credit Note"}
    template_name = os.path.join("invoicing", "create_credit_note.html")
    model = CreditNote
    form_class = forms.CreditNoteForm


class CreditNoteDetailView( ConfigMixin, MultiPageDocument, DetailView):
    template_name = os.path.join('invoicing', 'invoice', 'credit_note', 'detail.html')
    model = CreditNote
    
    page_length=16

    def get_multipage_queryset(self):
        return CreditNoteLine.objects.filter(note=CreditNote.objects.get(
            pk=self.kwargs['pk']))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Credit Note'
        context['pdf_link'] = True
        return context

#Deprecated
#credit notes now accessed on an invoice by invoice basis
class CreditNoteListView( ContextMixin, PaginationMixin, FilterView):
    extra_context = {"title": "List of Credit Notes"}
    template_name = os.path.join("invoicing", "invoice", "credit_note", "list.html")
    filterset_class = filters.CreditNoteFilter
    paginate_by = 20

    def get_queryset(self):
        return CreditNote.objects.all().order_by('date').reverse()


class CreditNotePDFView(ConfigMixin, MultiPageDocument, PDFDetailView):
    model = CreditNote
    template_name = os.path.join('invoicing', 'invoice', 'credit_note', 'pdf.html')
    file_name = "credit note.pdf"
    page_length=16

    def get_multipage_queryset(self):
        return CreditNoteLine.objects.filter(note=CreditNote.objects.get(
            pk=self.kwargs['pk']))
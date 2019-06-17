# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView
from django_filters.views import FilterView
from rest_framework import viewsets
from wkhtmltopdf import utils as pdf_tools
from wkhtmltopdf.views import PDFTemplateView

from common_data.forms import SendMailForm
from common_data.models import GlobalConfig
from common_data.utilities import ConfigMixin, ContextMixin, MultiPageDocument
from common_data.views import EmailPlusPDFView, PaginationMixin
from invoicing import filters, forms, serializers
from invoicing.models import *
from invoicing.views.invoice_views.util import InvoiceCreateMixin
from common_data.views import CREATE_TEMPLATE
from inventory.forms import ShippingAndHandlingForm
from common_data.forms import AuthenticateForm
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect

def process_data(items, inv):
    if items:
        items = json.loads(urllib.parse.unquote(items))
        for item in items:
            inv.add_line(item)
            

class QuotationCreateView(ContextMixin,
        InvoiceCreateMixin, 
        ConfigMixin, 
        CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","quotation", "create.html")
    form_class = forms.QuotationForm
    extra_context = {
        'box_array': 
            urllib.parse.quote(json.dumps([{
                "model": "customer",
                "app": "invoicing",
                "id": "id_customer"
            }]))
        
    }
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        
        if not self.object:
            return resp
            
        inv = self.object
        items = request.POST.get("item_list", None)
        process_data(items, inv)

        return resp

    def get_initial(self):
        initial = {}
        config = SalesConfig.objects.first()

        if self.kwargs.get('customer', None):
            initial['customer'] = self.kwargs['customer']
        initial.update({
            "status": "quotation",
            'terms': config.default_terms,
            'comments': config.default_quotation_comments
        })
        return initial

class QuotationUpdateView(UpdateView):
    template_name = os.path.join('invoicing', 'quotation', 'create.html')
    model =Invoice
    form_class = forms.QuotationForm
    

class QuotaionDetailView(ContextMixin, 
                            ConfigMixin, 
                            MultiPageDocument, 
                            DetailView):
    model = Invoice
    template_name = os.path.join("invoicing", "quotation",
        'detail.html')
    page_length = 16
    extra_context = {
        'pdf_link': True,
        'validate_form': AuthenticateForm()
    }
    
    def get_multipage_queryset(self):
        return InvoiceLine.objects.filter(invoice=Invoice.objects.get(pk=self.kwargs['pk']))

class QuotationPDFView(ConfigMixin, MultiPageDocument, PDFTemplateView):
    template_name = os.path.join("invoicing", "quotation",
        'pdf.html')
    file_name = 'invoice.pdf'
    page_length = 16
    
    def get_multipage_queryset(self):
        return InvoiceLine.objects.filter(invoice=Invoice.objects.get(pk=self.kwargs['pk']))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object'] = Invoice.objects.get(pk=self.kwargs['pk'])
        return context

class QuotationEmailSendView(EmailPlusPDFView):
    inv_class = Invoice
    success_url = reverse_lazy('invoicing:invoice-list')
    pdf_template_name = os.path.join("invoicing", "quotation",
            'pdf.html')

def make_invoice_from_quotation(request, pk=None):
    inv = get_object_or_404(Invoice, pk=pk)
    inv.status = "invoice"
    inv.draft = True
    inv.save()

    return HttpResponseRedirect(f'/invoicing/invoice-update/{pk}')

def make_proforma_from_quotation(request, pk=None):
    inv = get_object_or_404(Invoice, pk=pk)
    inv.status = "proforma"
    inv.draft = True
    inv.save()

    return HttpResponseRedirect(f'/invoicing/invoice-update/{pk}')
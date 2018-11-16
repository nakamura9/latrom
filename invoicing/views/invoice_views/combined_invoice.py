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
from common_data.utilities import ConfigMixin, ExtraContext, apply_style
from common_data.views import EmailPlusPDFMixin, PaginationMixin
from inventory.models import Product
from invoicing import filters, forms, serializers
from invoicing.models import *
from invoicing.views.common import SalesRepCheckMixin
from invoicing.views.invoice_views.util import InvoiceInitialMixin


def process_data(items, inv):
    if items:
        items = json.loads(urllib.parse.unquote(items))
        for item in items:
            inv.add_line(item)
            
    # moved here because the invoice item data must first be 
    # saved in the database before inventory and entries 
    # can be created

    if inv.status == 'sent': 
        #inv.create_credit_entry()
        pass
    elif inv.status == 'paid':
        #inv.create_cash_entry()
        pass
    else:#includes drafts and quotations
        pass

class CombinedInvoiceListView(SalesRepCheckMixin, ExtraContext, PaginationMixin, FilterView):
    extra_context = {"title": "Combined Invoice List",
                    "new_link": reverse_lazy("invoicing:create-combined-invoice")}
    template_name = os.path.join("invoicing", "combined_invoice","list.html")
    filterset_class = filters.CombinedInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return CombinedInvoice.objects.filter(active=True).order_by('date')
    

class CombinedInvoiceAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CombinedInvoiceSerializer
    queryset = CombinedInvoice.objects.all()

class CombinedInvoiceDetailView(SalesRepCheckMixin, ConfigMixin, DetailView):
    model = CombinedInvoice
    template_name = os.path.join("invoicing", "combined_invoice",
        'detail.html')

        
class CombinedInvoiceCreateView(SalesRepCheckMixin, InvoiceInitialMixin, ConfigMixin, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","combined_invoice", "create.html")
    form_class = forms.CombinedInvoiceForm
    success_url = reverse_lazy("invoicing:combined-invoice-list")


    def post(self, request, *args, **kwargs):
        resp = super(CombinedInvoiceCreateView, self).post(request, *args, **kwargs)
        
        if not self.object:
            return resp
            
        inv = self.object
        items = request.POST.get("item_list", None)
        process_data(items, inv)

        return resp

class CombinedInvoiceUpdateView(ExtraContext, UpdateView):
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:combined-invoice-list')
    model =CombinedInvoice
    form_class = forms.CombinedInvoiceUpdateForm
    extra_context = {
        'title': 'Update Combined Invoice'
    }

class CombinedInvoiceDraftUpdateView(SalesRepCheckMixin, ConfigMixin, UpdateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","combined_invoice", "create.html")
    form_class = forms.CombinedInvoiceForm
    success_url = reverse_lazy("invoicing:combined-invoice-list")
    model = CombinedInvoice

    def post(self, request, *args, **kwargs):
        resp = super(CombinedInvoiceDraftUpdateView, self).post(request, *args, **kwargs)
        
        if not self.object:
            return resp

        #remove existing items
        for line in self.object.combinedinvoiceline_set.all():
            line.delete()
        
        inv = self.object
        items = request.POST.get("item_list", None)
        
        process_data(items, inv)

        return resp

class CombinedInvoicePaymentView(ExtraContext, CreateView):
    model = Payment
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.CombinedInvoicePaymentForm
    success_url = reverse_lazy('invoicing:combined-invoice-list')
    extra_context= {
        'title': 'Apply Payment to Combined Invoice'
    }

    def get_initial(self):
        return {
            'combined_invoice': self.kwargs['pk'],
            'payment_for': 3
            }


class CombinedInvoicePaymentDetailView(ListView):
    template_name = os.path.join('invoicing', 'combined_invoice', 
        'payment', 'detail.html')

    def get_queryset(self):
        return Payment.objects.filter(combined_invoice=CombinedInvoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(CombinedInvoicePaymentDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = CombinedInvoice.objects.get(pk=self.kwargs['pk'])
        return context


class CombinedInvoicePDFView(ConfigMixin, PDFTemplateView):
    template_name = os.path.join("invoicing", "combined_invoice",
        'pdf.html')
    file_name = 'combined_invoice.pdf'
    def get_context_data(self, *args, **kwargs):
        context = super(CombinedInvoicePDFView, self).get_context_data(*args, **kwargs)
        context['object'] = CombinedInvoice.objects.get(pk=self.kwargs['pk'])
        return context

class CombinedInvoiceEmailSendView(EmailPlusPDFMixin):
    inv_class = CombinedInvoice
    success_url = reverse_lazy('invoicing:combined-invoice-list')
    pdf_template_name = os.path.join("invoicing", "combined_invoice",
            'pdf.html')

class CombinedInvoiceDraftDeleteView(SalesRepCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('invoicing:home')
    model = CombinedInvoice
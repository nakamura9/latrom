# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.core.mail import EmailMessage
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework import viewsets
from wkhtmltopdf import utils as pdf_tools
from wkhtmltopdf.views import PDFTemplateView

from common_data.forms import SendMailForm
from common_data.models import GlobalConfig
from common_data.utilities import ConfigMixin, ExtraContext, apply_style
from common_data.views import EmailPlusPDFMixin, PaginationMixin
from invoicing import filters, forms, serializers
from invoicing.models import *
from invoicing.views.common import SalesRepCheckMixin


def process_data(items, inv):
    if items:
        items = json.loads(urllib.parse.unquote(items))
        for item in items:
            inv.add_line(item['id'], item['hours'])
                
        # moved here because the invoice item data must first be 
        # saved in the database before inventory and entries 
        # can be created
        
    if inv.status == 'sent': 
        pass
        #inv.create_credit_entry()
    elif inv.status == 'paid':
        pass
        #inv.create_cash_entry()
    else:#includes drafts and quotations
        pass
        
class ServiceInvoiceAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ServiceInvoiceSerializer
    queryset = ServiceInvoice.objects.all()
class ServiceInvoiceListView(SalesRepCheckMixin, ExtraContext, PaginationMixin, FilterView):
    extra_context = {"title": "Service Invoice List",
                    "new_link": reverse_lazy("invoicing:create-service-invoice")}
    template_name = os.path.join("invoicing", "service_invoice","list.html")
    filterset_class = filters.AbstractInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return ServiceInvoice.objects.filter(active=True).order_by('date')
    

class ServiceInvoiceDetailView(SalesRepCheckMixin, ConfigMixin, DetailView):
    model = ServiceInvoice
    template_name = os.path.join("invoicing", "service_invoice",
        'detail.html')

class ServiceInvoiceUpdateView(ExtraContext, UpdateView):
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:service-invoice-list')
    model = ServiceInvoice
    form_class = forms.ServiceInvoiceUpdateForm
    extra_context = {
        'title': 'Update Service Invoice'
    }
class ServiceInvoiceCreateView(SalesRepCheckMixin, ConfigMixin, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","service_invoice", "create.html")
    form_class = forms.ServiceInvoiceForm
    success_url = reverse_lazy("invoicing:service-invoice-list")

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }


    def post(self, request, *args, **kwargs):
        resp = super(ServiceInvoiceCreateView, self).post(request, *args, **kwargs)
        
        if not self.object:
            return resp

        inv = self.object
        items = request.POST.get("item_list", None)
        
        process_data(items, inv)

        return resp


class ServiceDraftUpdateView(SalesRepCheckMixin, ConfigMixin, UpdateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","service_invoice", "create.html")
    form_class = forms.ServiceInvoiceForm
    success_url = reverse_lazy("invoicing:service-invoice-list")
    model = ServiceInvoice


    def post(self, request, *args, **kwargs):
        resp = super(ServiceDraftUpdateView, self).post(request, *args, **kwargs)
        
        if not self.object:
            return resp

        #remove existing items
        for line in self.object.serviceinvoiceline_set.all():
            line.delete()
        
        inv = self.object
        items = request.POST.get("item_list", None)
        
        process_data(items, inv)

        return resp

class ServiceInvoicePaymentView(ExtraContext, CreateView):
    model = Payment
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.ServiceInvoicePaymentForm
    success_url = reverse_lazy('invoicing:service-invoice-list')
    extra_context= {
        'title': 'Apply Payment to Service Invoice'
    }

    def get_initial(self):
        return {
            'service_invoice': self.kwargs['pk'],
            'payment_for': 1
            }


class ServiceInvoicePaymentDetailView(ListView):
    template_name = os.path.join('invoicing', 'service_invoice', 
        'payment', 'detail.html')

    def get_queryset(self):
        return Payment.objects.filter(service_invoice=ServiceInvoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(ServiceInvoicePaymentDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = ServiceInvoice.objects.get(pk=self.kwargs['pk'])
        return context


class ServiceInvoicePDFView(ConfigMixin, PDFTemplateView):
    template_name = os.path.join("invoicing", "service_invoice",
        'pdf.html')
    file_name = 'service_invoice.pdf'
    def get_context_data(self, *args, **kwargs):
        context = super(ServiceInvoicePDFView, self).get_context_data(*args, **kwargs)
        context['object'] = ServiceInvoice.objects.get(pk=self.kwargs['pk'])
        return context

class ServiceInvoiceEmailSendView(EmailPlusPDFMixin):
    inv_class = ServiceInvoice
    pdf_template_name = os.path.join("invoicing", "service_invoice",
            'pdf.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')
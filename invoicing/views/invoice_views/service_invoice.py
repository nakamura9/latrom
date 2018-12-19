# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.core.mail import EmailMessage
from django.contrib import messages
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
from invoicing.views.invoice_views.util import InvoiceCreateMixin

class ServiceInvoiceMixin(object):
    def post(self, request, *args, **kwargs):
        if isinstance(self, UpdateView):
            self.object = self.get_object()
            #if an existing object is saved as a draft again
            # if an existing object is saved from draft to quote or invoice
            if self.object.status == "draft":
                resp = super().post(request, *args, **kwargs)

                item_string = request.POST.get('item_list', None)
                if not item_string or item_string =="":
                    messages.info(request, 'No items were added to this invoice. Please provide some data')
                else:
                    for line in self.object.serviceinvoiceline_set.all():
                        line.delete()

                    self.process_data(item_string)
            else:
                resp = super().post(request, *args, **kwargs)

        else:
            
            resp = super().post(request, *args, **kwargs)

            if not self.object:
                return resp
        
            #new invoice actions
            item_string = request.POST.get('item_list', None)
            if not item_string:
                messages.info(request, 'No items were added to this invoice. Please provide some data')
            self.process_data(item_string)

        #valid for both new and existing invoices
        if self.object.status in ["invoice", 'paid']:
            self.object.create_entry()#if existing method returns none

        self.set_payment_amount()
        return resp

    def process_data(self, items):
        if items:
            items = json.loads(urllib.parse.unquote(items))
            for item in items:

                self.object.add_line(item['service'].split('-')[0], item['hours'])
                
        # moved here because the invoice item data must first be 
        # saved in the database before inventory and entries 
        # can be created
        
class ServiceInvoiceAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ServiceInvoiceSerializer
    queryset = ServiceInvoice.objects.all()

class ServiceInvoiceListView(SalesRepCheckMixin, ExtraContext, PaginationMixin,
        FilterView):
    extra_context = {"title": "Service Invoice List",
                    "new_link": reverse_lazy("invoicing:create-service-invoice")}
    template_name = os.path.join("invoicing", "service_invoice","list.html")
    filterset_class = filters.ServiceInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return ServiceInvoice.objects.all()
    

class ServiceInvoiceDetailView(SalesRepCheckMixin, ConfigMixin, DetailView):
    model = ServiceInvoice
    template_name = os.path.join("invoicing", "service_invoice",
        'detail.html')

class ServiceInvoiceUpdateView(SalesRepCheckMixin, 
                                InvoiceCreateMixin, 
                                ExtraContext, 
                                ServiceInvoiceMixin, 
                                UpdateView):
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:service-invoice-list')
    model = ServiceInvoice
    form_class = forms.ServiceInvoiceUpdateForm
    extra_context = {
        'title': 'Update Service Invoice'
    }
class ServiceInvoiceCreateView(SalesRepCheckMixin, 
                                ServiceInvoiceMixin, 
                                InvoiceCreateMixin, 
                                ConfigMixin, 
                                CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","service_invoice", "create.html")
    form_class = forms.ServiceInvoiceForm
    success_url = reverse_lazy("invoicing:service-invoice-list")
    payment_for = 1


class ServiceDraftUpdateView(SalesRepCheckMixin,
                            InvoiceCreateMixin,         
                            ServiceInvoiceMixin, 
                            ConfigMixin, 
                            UpdateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","service_invoice", "create.html")
    form_class = forms.ServiceInvoiceForm
    success_url = reverse_lazy("invoicing:service-invoice-list")
    model = ServiceInvoice


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

    def post(self, *args, **kwargs):
        resp = super().post(*args, **kwargs)
        if self.object:
            self.object.create_entry()

        return resp

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

class ServiceInvoiceDraftDeleteView(SalesRepCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('invoicing:home')
    model = ServiceInvoice
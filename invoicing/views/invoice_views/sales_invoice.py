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
            pk, name = item['item_name'].split('-')
            inv.add_product(Product.objects.get(pk=pk), 
                item['quantity'])
    
    # moved here because the invoice item data must first be 
    # saved in the database before inventory and entries 
    # can be created
    if inv.status in ['draft', 'quotation']:
        pass
    elif inv.status == 'sent': 
        pass
        #inv.update_inventory()
        #inv.create_credit_entry()
    elif inv.status == 'paid':
        pass
        #inv.update_inventory()
        #inv.create_cash_entry()
    else:
        pass

class SalesInvoiceListView(SalesRepCheckMixin, ExtraContext, PaginationMixin, 
        FilterView):
    extra_context = {"title": "Sales Invoice List",
                    "new_link": reverse_lazy("invoicing:create-sales-invoice")}
    template_name = os.path.join("invoicing", "sales_invoice","list.html")
    filterset_class = filters.SalesInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return SalesInvoice.objects.filter(active=True).order_by('date')
    

class SalesInvoiceDetailView(SalesRepCheckMixin, ConfigMixin, DetailView):
    model = SalesInvoice
    template_name = os.path.join("invoicing", "sales_invoice",
        'detail.html')
    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoiceDetailView, self).get_context_data(*args, **kwargs)
        context['title'] = context.get('invoice_title', "Invoice")
        return context

        
class SalesInvoiceCreateView(SalesRepCheckMixin, InvoiceInitialMixin, ExtraContext, ConfigMixin, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    extra_context = {
        "title": "Create a New Invoice"
        }
            
    template_name = os.path.join("invoicing","sales_invoice", "create.html")
    form_class = forms.SalesInvoiceForm
    success_url = reverse_lazy("invoicing:sales-invoice-list")
    model = SalesInvoice

    def post(self, request, *args, **kwargs):
        resp = super(SalesInvoiceCreateView, self).post(request, *args, **kwargs)
        if not self.object:
            return resp

        inv = self.object
        
        items = request.POST.get("item_list", None)
        process_data(items, inv)
        #fix 
        #create payment for invoice and entry if the post obj is paid
        return resp


class SalesDraftUpdateView(SalesRepCheckMixin, ConfigMixin, UpdateView):
    model = SalesInvoice
    form_class = forms.SalesInvoiceForm
    template_name = os.path.join('invoicing', 'sales_invoice','create.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')

    def post(self, request, *args, **kwargs):
        resp = super(SalesDraftUpdateView, self).post(request, *args, **kwargs)

        #remove existing lines
        for line in self.object.salesinvoiceline_set.all():
            line.delete()
        #create new lines 
        items = request.POST.get("item_list", None)
        
        process_data(items, self.object)

        return resp


class SalesInvoiceUpdateView(SalesRepCheckMixin, ExtraContext, UpdateView):
    extra_context = {
        'title': 'Edit Sales Invoice Details'
    }
    model = SalesInvoice
    form_class = forms.SalesInvoiceUpdateForm
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')


def apply_full_payment_on_invoice(request):
    pass


class SalesInvoiceAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SalesInvoiceSerializer
    queryset = SalesInvoice.objects.all()


class SalesInvoicePaymentView(SalesRepCheckMixin,ExtraContext, CreateView):
    model = Payment
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.SalesInvoicePaymentForm
    success_url = reverse_lazy('invoicing:sales-invoice-list')
    extra_context= {
        'title': 'Apply Payment to Sales Invoice'
    }

    def get_initial(self):
        return {
            'sales_invoice': self.kwargs['pk'],
            'payment_for': 0
            }


class SalesInvoicePaymentDetailView(SalesRepCheckMixin, ListView):
    template_name = os.path.join('invoicing', 'sales_invoice', 
        'payment', 'detail.html')

    def get_queryset(self):
        return Payment.objects.filter(sales_invoice=SalesInvoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoicePaymentDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        return context


class SalesInvoiceReturnsDetailView(SalesRepCheckMixin, ListView):
    template_name = os.path.join('invoicing', 'sales_invoice', 
        'credit_note', 'detail_list.html')

    def get_queryset(self):
        return CreditNote.objects.filter(invoice=SalesInvoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoiceReturnsDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        return context


class SalesInvoicePDFView(ConfigMixin, PDFTemplateView):
    template_name = os.path.join("invoicing", "sales_invoice",
        'pdf.html')
    file_name = 'sales_invoice.pdf'
    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoicePDFView, self).get_context_data(*args, **kwargs)
        context['object'] = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        return context

class SalesInvoiceEmailSendView(SalesRepCheckMixin, EmailPlusPDFMixin):
    inv_class = SalesInvoice
    pdf_template_name = os.path.join("invoicing", "sales_invoice",
            'pdf.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')


class SalesInvoiceDraftDeleteView(SalesRepCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('invoicing:home')
    model = SalesInvoice
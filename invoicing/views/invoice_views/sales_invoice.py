# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.core.mail import EmailMessage
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, 
                                        FormView, 
                                        UpdateView, 
                                        DeleteView)

from common_data.utilities import MultiPageDocument
from django.http import HttpResponseRedirect
from django_filters.views import FilterView
from rest_framework import viewsets
from wkhtmltopdf import utils as pdf_tools
from wkhtmltopdf.views import PDFTemplateView

from common_data.forms import SendMailForm
from common_data.models import GlobalConfig
from common_data.utilities import ConfigMixin, ContextMixin, apply_style
from common_data.views import EmailPlusPDFView, PaginationMixin
from inventory.forms import ShippingAndHandlingForm
from invoicing import filters, forms, serializers
from invoicing.models import *
from invoicing.views.invoice_views.util import InvoiceCreateMixin
from accounting.models import Expense, Account

CREATE_TEMPLATE = os.path.join("common_data", "create_template.html")


class SalesInvoiceMixin(object):
    def post(self, request, *args, **kwargs):
        if isinstance(self, UpdateView):
            #update actions 
            self.object = self.get_object()
            if self.object.status == "draft":
                resp = super().post(request, *args, **kwargs)

                item_string = request.POST.get('item_list', None)
                if not item_string or item_string == "":
                    messages.info(request, 'No items were added to this invoice. Please provide some data')
                else:
                    for line in self.object.salesinvoiceline_set.all():
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
            self.object.create_entry()

        self.set_payment_amount()
        return resp

    def process_data(self, items):
        if items:
            items = json.loads(urllib.parse.unquote(items))
            for item in items:
                pk = item['product'].split('-')[0]
                self.object.add_product(Product.objects.get(pk=pk), 
                    item['quantity'])
    

class SalesInvoiceListView( ContextMixin, PaginationMixin, 
        FilterView):
    extra_context = {"title": "Sales Invoice List",
                    "new_link": reverse_lazy("invoicing:create-sales-invoice")}
    template_name = os.path.join("invoicing", "sales_invoice","list.html")
    filterset_class = filters.SalesInvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return SalesInvoice.objects.filter(
            active=True).order_by('date').reverse()
    

class SalesInvoiceDetailView( ConfigMixin, MultiPageDocument, DetailView):
    model = SalesInvoice
    template_name = os.path.join("invoicing", "sales_invoice",
        'detail.html')
    page_length =16

    def get_multipage_queryset(self):
        return SalesInvoiceLine.objects.filter(invoice=SalesInvoice.objects.get(pk=self.kwargs['pk']))
        
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = context.get('invoice_title', "Invoice")
        
        if self.object.status == "draft":
            shortages = self.object.verify_inventory()
            
            context['notes'] = [
                'There is insufficient quantity of product <u>{}</u> from warehouse <u>{}</u>. The additional inventory required is <b>{}</b> units.'.format(
                    shortage['product'], 
                    self.object.ship_from, 
                    shortage['quantity']
                    ) for shortage in shortages
                ]

            actions = [
                {
                    'name': 'Verify as quotation',
                    'url': '/invoicing/sales-invoice/{}/verify/quotation'.format(
                        self.object.pk)
                },
                {
                    'name': 'Verify as invoice',
                    'url': '/invoicing/sales-invoice/{}/verify/invoice'.format(
                        self.object.pk)
                },
            ] 
            if len(shortages) > 0:
                actions += [
                    {
                        'name': 'Order Additional Inventory',
                        'url': '/inventory/order-create'
                    },
                    {
                        'name': 'Manage Warehouses',
                        'url': '/inventory/warehouse-list/'
                    }
                ]
            context['actions'] = actions

        return context

        
class SalesInvoiceCreateView( 
        SalesInvoiceMixin, 
        InvoiceCreateMixin, 
        ContextMixin, 
        ConfigMixin, 
        CreateView):
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
    payment_for = 0


class SalesDraftUpdateView( 
                            InvoiceCreateMixin,
                            SalesInvoiceMixin, 
                            ConfigMixin, 
                            UpdateView):
    model = SalesInvoice
    form_class = forms.SalesInvoiceForm
    template_name = os.path.join('invoicing', 'sales_invoice','create.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')


class SalesInvoiceUpdateView( 
                            ContextMixin, 
                            InvoiceCreateMixin,
                            UpdateView):
    extra_context = {
        'title': 'Edit Sales Invoice Details'
    }
    model = SalesInvoice
    form_class = forms.SalesInvoiceUpdateForm
    template_name = os.path.join('common_data', 'create_template.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')



class SalesInvoiceAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SalesInvoiceSerializer
    queryset = SalesInvoice.objects.all()


class SalesInvoicePaymentView(ContextMixin, CreateView):
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

    def post(self, *args, **kwargs):
        resp = super().post(*args, **kwargs)
        if self.object:
            self.object.create_entry()

        return resp


class SalesInvoicePaymentDetailView( ListView):
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


class SalesInvoiceReturnsDetailView( ListView):
    template_name = os.path.join('invoicing', 'sales_invoice', 
        'credit_note', 'detail_list.html')

    def get_queryset(self):
        return CreditNote.objects.filter(invoice=SalesInvoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(
            *args, **kwargs
        )
        context['invoice'] = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        return context


class SalesInvoicePDFView(ConfigMixin, MultiPageDocument, PDFTemplateView):
    template_name = os.path.join("invoicing", "sales_invoice",
        'pdf.html')
    file_name = 'sales_invoice.pdf'
    page_length =16
    def get_context_data(self, *args, **kwargs):
        context = super(SalesInvoicePDFView, self).get_context_data(*args, **kwargs)
        context['object'] = SalesInvoice.objects.get(pk=self.kwargs['pk'])
        return context

    def get_multipage_queryset(self):
        return SalesInvoiceLine.objects.filter(invoice=SalesInvoice.objects.get(pk=self.kwargs['pk']))

class SalesInvoiceEmailSendView( EmailPlusPDFView):
    inv_class = SalesInvoice
    pdf_template_name = os.path.join("invoicing", "sales_invoice",
            'pdf.html')
    success_url = reverse_lazy('invoicing:sales-invoice-list')


class SalesInvoiceDraftDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('invoicing:home')
    model = SalesInvoice

def verify_invoice(request, pk=None, status=None):
    inv = get_object_or_404(SalesInvoice, pk=pk)
    inv.status = status
    inv.save()

    if inv.status == "invoice":
        inv.create_entry()

    return HttpResponseRedirect('/invoicing/sales-invoice-detail/{}'.format(pk))


# TODO test
class ShippingAndHandlingView( 
        ContextMixin, FormView):
    template_name = CREATE_TEMPLATE
    form_class = ShippingAndHandlingForm
    success_url = reverse_lazy("invoicing:sales-invoice-list")
    extra_context = {
        'title': 'Record Shipping and handling'
    }

    def get_initial(self):
        return {
            'reference': 'SINV{}'.format(self.kwargs['pk'])
        }
    
    def form_valid(self, form):
        resp =  super().form_valid(form)

        invoice = SalesInvoice.objects.get(pk=self.kwargs['pk'])


        expense = Expense.objects.create(
            category=11,
            amount=form.cleaned_data['amount'],
            description=form.cleaned_data['description'],
            debit_account=Account.objects.get(pk=1000),#cash
            recorded_by=form.cleaned_data['recorded_by'],
            date=form.cleaned_data['date']
        )

        expense.create_entry()
        invoice.shipping_expenses.add(expense)
        invoice.save()#necessary?

        return resp

class ShippingExpenseListView(DetailView):
    model = SalesInvoice
    template_name = os.path.join("invoicing", "sales_invoice", 
        "shipping_list.html")

        
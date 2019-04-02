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


class InvoiceListView( ContextMixin, PaginationMixin, FilterView):
    extra_context = {"title": "Quotation + Invoice List",
                    "new_link": reverse_lazy("invoicing:create-invoice")}
    template_name = os.path.join("invoicing", "invoice","list.html")
    filterset_class = filters.InvoiceFilter
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(active=True).order_by('date').reverse()
    

class InvoiceAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.InvoiceSerializer
    queryset = Invoice.objects.all()

class InvoiceDetailView(ContextMixin, ConfigMixin, MultiPageDocument, DetailView):
    model = Invoice
    template_name = os.path.join("invoicing", "invoice",
        'detail.html')
    page_length = 16
    extra_context = {
        'pdf_link': True,
        'validate_form': AuthenticateForm()
    }
    
    def get_multipage_queryset(self):
        return InvoiceLine.objects.filter(invoice=Invoice.objects.get(pk=self.kwargs['pk']))

        
class InvoiceCreateView( InvoiceCreateMixin, ConfigMixin, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''

            
    template_name = os.path.join("invoicing","invoice", "create.html")
    form_class = forms.InvoiceForm
    success_url = reverse_lazy("invoicing:invoices-list")

    def get_initial(self):
        initial = {}
        if self.kwargs.get('customer', None):
            initial['customer'] = self.kwargs['customer']
        initial.update({
            "status": "invoice"
        })
        return initial

    def post(self, request, *args, **kwargs):
        resp = super(InvoiceCreateView, self).post(request, *args, **kwargs)
        
        if not self.object:
            return resp
            
        inv = self.object
        items = request.POST.get("item_list", None)
        process_data(items, inv)        
        return resp

class InvoiceUpdateView(ContextMixin, UpdateView):
    template_name = os.path.join('invoicing', 'invoice', 'create.html')
    success_url = reverse_lazy('invoicing:invoices-list')
    model =Invoice
    form_class = forms.InvoiceUpdateForm
    extra_context = {
        'title': 'Update  Invoice'
    }


    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        
        if not self.object:
            return resp

        if not self.object.draft:
            return resp
        #remove existing items
        for line in self.object.invoiceline_set.all():
            line.delete()
        
        inv = self.object
        items = request.POST.get("item_list", None)
        
        process_data(items, inv)

        if self.object.status in ["invoice", 'paid']:
            self.object.create_entry()

        return resp

class InvoicePaymentView(ContextMixin, CreateView):
    model = Payment
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.InvoicePaymentForm
    success_url = reverse_lazy('invoicing:invoices-list')
    extra_context= {
        'title': 'Apply Payment to  Invoice'
    }

    def get_initial(self):
        return {
            'invoice': self.kwargs['pk'],
            }

    def post(self, *args, **kwargs):
        resp = super().post(*args, **kwargs)
        if self.object:
            self.object.create_entry()

        return resp


class InvoicePaymentDetailView(ListView):
    template_name = os.path.join('invoicing', 'invoice', 
        'payment', 'detail.html')

    def get_queryset(self):
        return Payment.objects.filter(invoice=Invoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(
            *args, **kwargs
        )
        context['invoice'] = Invoice.objects.get(pk=self.kwargs['pk'])
        return context


class InvoicePDFView(ConfigMixin, MultiPageDocument, PDFTemplateView):
    template_name = os.path.join("invoicing", "invoice",
        'pdf.html')
    file_name = 'invoice.pdf'
    page_length = 16
    
    def get_multipage_queryset(self):
        return InvoiceLine.objects.filter(invoice=Invoice.objects.get(pk=self.kwargs['pk']))

    def get_context_data(self, *args, **kwargs):
        context = super(InvoicePDFView, self).get_context_data(*args, **kwargs)
        context['object'] = Invoice.objects.get(pk=self.kwargs['pk'])
        return context

class InvoiceEmailSendView(EmailPlusPDFView):
    inv_class = Invoice
    success_url = reverse_lazy('invoicing:invoice-list')
    pdf_template_name = os.path.join("invoicing", "invoice",
            'pdf.html')

class InvoiceDraftDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('invoicing:home')
    model = Invoice


class InvoiceReturnsDetailView( ListView):
    template_name = os.path.join('invoicing', 'invoice', 
        'credit_note', 'detail_list.html')

    def get_queryset(self):
        return CreditNote.objects.filter(invoice=Invoice.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(
            *args, **kwargs
        )
        context['invoice'] = Invoice.objects.get(pk=self.kwargs['pk'])
        return context

class InvoiceDraftDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('invoicing:home')
    model = Invoice

def verify_invoice(request, pk=None):
    inv = get_object_or_404(Invoice, pk=pk)
    if inv.status == "quotation":
        inv.draft = False
        inv.save()
        return HttpResponseRedirect('/invoicing/quotation-detail/{}'.format(pk))

    form = AuthenticateForm(request.POST)
    
    if form.is_valid():
        inv.draft = False
        inv.save()

        if inv.status == "invoice":
            inv.create_entry()
            inv.invoice_validated_by = form.cleaned_data['user']
            inv.save()

    return HttpResponseRedirect('/invoicing/invoice-detail/{}'.format(pk))


# TODO test
class ShippingAndHandlingView( 
        ContextMixin, FormView):
    template_name = CREATE_TEMPLATE
    form_class = ShippingAndHandlingForm
    success_url = reverse_lazy("invoicing:invoices-list")
    extra_context = {
        'title': 'Record Shipping and handling'
    }

    def get_initial(self):
        return {
            'reference': 'SINV{}'.format(self.kwargs['pk'])
        }
    
    def form_valid(self, form):
        resp =  super().form_valid(form)

        invoice = Invoice.objects.get(pk=self.kwargs['pk'])


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
    model = Invoice
    template_name = os.path.join("invoicing", "invoice", 
        "shipping_list.html")
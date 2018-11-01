# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django_filters.views import FilterView
from rest_framework import viewsets
from wkhtmltopdf.views import PDFTemplateView

from common_data.models import GlobalConfig
from common_data.utilities import ConfigMixin, ExtraContext, apply_style
from common_data.views import EmailPlusPDFMixin, PaginationMixin
from inventory.models import Product
from invoicing import filters, forms, serializers
from invoicing.models import *
from invoicing.views.common import SalesRepCheckMixin
from invoicing.views.invoice_views.util import InvoiceInitialMixin


def process_data(data, inv):
    items = json.loads(urllib.parse.unquote(data))
    for item in items:
        inv.add_line(item['pk'])
    
    # moved here because the invoice item data must first be 
    # saved in the database before inventory and entries 
    # can be created
    if inv.status in ['draft', 'quotation']:
        pass
    elif inv.status in ['sent', 'paid']: 
        inv.create_entry()
    else:
        pass


class BillListView(SalesRepCheckMixin, ExtraContext, PaginationMixin, FilterView):
    extra_context = {"title": "Customer Bill List",
                    "new_link": reverse_lazy("invoicing:bill-create")}
    template_name = os.path.join("invoicing", "bill","list.html")
    filterset_class = filters.BillInvoiceFilter
    paginate_by = 10

    queryset = Bill.objects.filter(active=True).order_by('date')
    

class BillDetailView(SalesRepCheckMixin, ConfigMixin, DetailView):
    model = Bill
    template_name = os.path.join("invoicing", "bill",
        'detail.html')

        
class BillCreateView(SalesRepCheckMixin, InvoiceInitialMixin, ConfigMixin, CreateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    
    template_name = os.path.join("invoicing","bill", "create.html")
    form_class = forms.BillForm
    success_url = reverse_lazy("invoicing:bills-list")


    def get_context_data(self, *args, **kwargs):
        context = super(BillCreateView, self).get_context_data(*args, **kwargs)
        context.update({'include_customer': True})
        return context

    def post(self, request, *args, **kwargs):
        #check if an expense has been recorded
        data = request.POST.get("item_list", None)
        if not data:
            messages.error(self.request, 'No data was sent to the server. Please provide items to the bill.')
            return HttpResponseRedirect(reverse_lazy('invoicing:bill-create'))
        else:
            items = json.loads(urllib.parse.unquote(data))
            if isinstance(items, list) or len(items) < 1:
                messages.error(self.request, 'The provided data could not be processed by the server. Please provide items to the bill.')
                return HttpResponseRedirect(reverse_lazy('invoicing:bill-create'))

        resp = super(BillCreateView, self).post(request, *args, **kwargs)
        if not self.object:
            return resp
        inv = self.object
        
        process_data(data, inv)
        return resp

class BillDraftUpdateView(SalesRepCheckMixin,ConfigMixin, UpdateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    
    template_name = os.path.join("invoicing","bill", "create.html")
    form_class = forms.BillUpdateForm
    success_url = reverse_lazy("invoicing:bills-list")
    model = Bill

    def get_initial(self):
        config = SalesConfig.objects.first()
        return {
            'terms': config.default_terms,
            'comments': config.default_invoice_comments
        }

    def post(self, request, *args, **kwargs):
        resp = super(BillDraftUpdateView, self).post(request, *args, **kwargs)
        if not self.object:
            return resp
        inv = self.object
        for line in inv.billline_set.all():
            line.delete()
        data = request.POST.get("item_list", None)
        process_data(data, inv)
        return resp


class BillUpdateView(ExtraContext, SalesRepCheckMixin, UpdateView):
    '''Quotes and Invoices are created with React.js help.
    data is shared between the static form and django by means
    of a json urlencoded string stored in a list of hidden input 
    fields called 'items[]'. '''
    
    template_name = os.path.join("common_data", "create_template.html")
    form_class = forms.BillUpdateForm
    success_url = reverse_lazy("invoicing:home")
    model = Bill
    extra_context ={
        'title': 'Update Bill'
    }


class BillAPIViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BillSerializer
    queryset = Bill.objects.all()


class BillPaymentView(ExtraContext, CreateView):
    model = Payment
    template_name = os.path.join('common_data', 'create_template.html')
    form_class = forms.BillPaymentForm
    success_url = reverse_lazy('invoicing:bills-list')
    extra_context= {
        'title': 'Apply Payment for Customer Bill'
    }

    def get_initial(self):
        return {
            'bill': self.kwargs['pk'],
            'payment_for': 2
            }


class BillPaymentDetailView(ListView):
    template_name = os.path.join('invoicing', 'bill', 
        'payment', 'detail.html')

    def get_queryset(self):
        return Payment.objects.filter(bill=Bill.objects.get(
            pk=self.kwargs['pk']
        ))

    def get_context_data(self, *args, **kwargs):
        context = super(BillPaymentDetailView, self).get_context_data(
            *args, **kwargs
        )
        context['invoice'] = Bill.objects.get(pk=self.kwargs['pk'])
        return context


class BillPDFView(ConfigMixin, PDFTemplateView):
    template_name = os.path.join("invoicing", "bill",
        'pdf.html')
    file_name = 'bill.pdf'
    def get_context_data(self, *args, **kwargs):
        context = super(BillPDFView, self).get_context_data(*args, **kwargs)
        context['object'] = Bill.objects.get(pk=self.kwargs['pk'])
        return context



class BillEmailSendView(EmailPlusPDFMixin):
    inv_class = Bill
    success_url = reverse_lazy('invoicing:bills-list')
    pdf_template_name = os.path.join('invoicing', 'bill', 'pdf.html')


import json
import os
import urllib
from decimal import Decimal as D

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import ModelViewSet

from common_data.models import GlobalConfig
from common_data.utilities import *
from common_data.views import PaginationMixin, PDFDetailView
from inventory import filters, forms, models, serializers
from invoicing.models import SalesConfig, InvoiceLine, Invoice
from accounting.models import Account, Journal, JournalEntry


class PurchaseReturnListView(ContextMixin, PaginationMixin, FilterView):
    '''List of Debit Notes'''
    template_name = os.path.join('inventory', 'dispatch', 'purchase_returns', 'list.html')
    filterset_class = filters.PurchaseReturnsFilter
    paginate_by = 20
    extra_context = {
        'title': 'List Of Purchase Returns'
    }

    def  get_queryset(self):
        warehouse = models.WareHouse.objects.get(pk=self.kwargs['warehouse'])
        return models.DebitNote.objects.filter(order__ship_to=warehouse)

class DeliveryNoteView(ContextMixin, ConfigMixin, DetailView):
    model = models.StockDispatch
    template_name = os.path.join('inventory', 'dispatch', 'delivery_note',
        'document.html')
    extra_context = {
        'pdf_link': True
    }
class DispatchPurchaseReturnsView(CreateView):
    form_class = forms.StockDispatchForm
    template_name = os.path.join('inventory', 'dispatch', 'purchase_returns',
        'create.html')

    def get_initial(self): 
        return {
            'request': models.DispatchRequest.objects.get(
                debit_note=self.kwargs['debit_note']).pk
        }
    
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        data = json.loads(urllib.parse.unquote(request.POST['sent-items']))
        print(data)
        for line in data:
            id = line['item'].split('-')[0]
            models.DispatchLine.objects.create(
                debit_line=models.DebitNoteLine.objects.get(pk=id),
                quantity = line['quantity'],
                dispatch=self.object
            )
        return resp


class InvoiceDispatchListView(ContextMixin, PaginationMixin, FilterView):
    '''List of Invoices '''
    template_name = os.path.join('inventory', 'dispatch', 'sales', 'list.html')
    filterset_class = filters.InvoiceDispatchFilter
    paginate_by = 20
    extra_context = {
        'title': 'List Of Invoices to Dispatch'
    }

    def  get_queryset(self):
        warehouse = models.WareHouse.objects.get(pk=self.kwargs['warehouse'])
        return Invoice.objects.filter(ship_from=warehouse)

class DispatchInvoiceView(CreateView):
    form_class = forms.StockDispatchForm
    template_name = os.path.join('inventory', 'dispatch', 'sales',
        'create.html')

    def get_initial(self): 
        return {
            'request': models.DispatchRequest.objects.get(
                invoice=self.kwargs['invoice']).pk
        }
    
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        data = json.loads(urllib.parse.unquote(request.POST['sent-items']))
        for line in data:
            id = line['item'].split('-')[0]
            models.DispatchLine.objects.create(
                invoice_line=InvoiceLine.objects.get(pk=id),
                quantity = line['quantity'],
                dispatch=self.object
            )
        return resp
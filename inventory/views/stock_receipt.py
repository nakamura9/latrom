
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
from invoicing.models import SalesConfig
from accounting.models import Account, Journal, JournalEntry

class TransferStockReceiptCreateView(CreateView):
    form_class = forms.IncomingTransferStockReceiptForm
    model = models.StockReceipt
    template_name = os.path.join("inventory", "goods_received",
        "stock_receipt.html")
    extra_context = {"title": "Receive Ordered goods"}

    def get_initial(self):
        warehouse = models.Order.objects.get(pk=self.kwargs['pk']).ship_to
        return {
            'transfer': self.kwargs['pk'],
            'warehouse': warehouse.pk
        }

class CreditNoteStockReceiptCreateView(CreateView):
    pass

class OrderStockReceiptCreateView(CreateView):
    form_class = forms.OrderStockReceiptForm
    model = models.StockReceipt
    template_name = os.path.join("inventory", "goods_received",
        "stock_receipt.html")
    extra_context = {"title": "Receive Ordered goods"}

    def get_initial(self):
        warehouse = models.Order.objects.get(pk=self.kwargs['pk']).ship_to
        return {
            'order': self.kwargs['pk'],
            'warehouse': warehouse.pk
        }

    def post(self, request, *args, **kwargs):
        resp = super(StockReceiptCreateView, self).post(request, *args, **kwargs)
        if not self.object:
            return resp

        data = json.loads(urllib.parse.unquote(request.POST['received-items']))
        subtotal = D(0)
        for line in data:
            pk = line['item'].split("-")[0]
            n = line['quantity_to_move']
            if n == 0:
                break

            if line['receiving_location'] != "":
                medium = line['receiving_location'].split('-')[0]
                item = models.OrderItem.objects.get(pk=pk)
                item.receive(n, medium=medium, receipt=self.object)
            else:
                item = models.OrderItem.objects.get(pk=pk)
                item.receive(n, receipt=self.object)

            subtotal += item.order_price * D(n)
        # Only credit supplier account the money we owe them for received 
        # inventory
        tax = subtotal * (D(self.object.order.tax.rate) / D(100))
        total = subtotal + tax
        entry = JournalEntry.objects.create(
            date = self.object.receive_date,
            memo = f"Order {self.object.order.pk} received ",
            journal = Journal.objects.get(pk=4),
            created_by = self.object.order.issuing_inventory_controller.employee.user,
            draft=False
        )

        if not self.object.order.supplier.account:
            self.object.order.supplier.create_account()
            
        entry.credit(total, self.object.order.supplier.account)
        entry.debit(subtotal, Account.objects.get(pk=4006))#purchases
        entry.debit(tax, Account.objects.get(pk=2001))#tax
        
        return resp 

class GoodsReceivedVoucherView(ContextMixin,
                               MultiPageDocument,
                               ConfigMixin, 
                               DetailView):
    model = models.StockReceipt
    page_length=20
    template_name = os.path.join("inventory", "goods_received", "voucher.html")
    extra_context ={
        'pdf_link': True
    }

    def get_multipage_queryset(self):
        return self.object.stockreceiptline_set.all()
        
class GoodsReceivedVoucherPDFView( ConfigMixin, PDFDetailView):
    template_name = os.path.join("inventory", "goods_received", "voucher.html")
    model = models.StockReceipt

class OrderGoodsReceiptsList(TemplateView):
    template_name=os.path.join('inventory','goods_received', 'list.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = models.Order.objects.get(
            pk=self.kwargs['pk'])

        return context 
    
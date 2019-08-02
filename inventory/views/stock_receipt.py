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
from invoicing.models import SalesConfig, CreditNote, CreditNoteLine

from accounting.models import Account, Journal, JournalEntry


#################################################
#                    Common                     #
#################################################

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
        
class GoodsReceivedVoucherPDFView(ConfigMixin, MultiPageDocument,PDFDetailView):
    template_name = os.path.join("inventory", "goods_received", "voucher.html")
    model = models.StockReceipt
    page_length=20

    def get_multipage_queryset(self):
        return self.object.stockreceiptline_set.all()



#################################################
#                  Orders                       #
#################################################
class IncomingOrderListView(ContextMixin, PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.OrderFilter
    template_name = os.path.join('inventory', 'incoming', 'order', 'list.html')
    extra_context = {
        'title': 'List of Incoming Orders.'
    }

    def get_queryset(self):
        warehouse = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return models.Order.objects.filter(ship_to=warehouse)

class OrderStockReceiptCreateView(CreateView):
    form_class = forms.OrderStockReceiptForm
    model = models.StockReceipt
    template_name = os.path.join("inventory", "incoming",
        'order' ,"create.html")
    extra_context = {"title": "Receive Ordered goods"}

    def get_initial(self):
        warehouse = models.Order.objects.get(pk=self.kwargs['pk']).ship_to
        return {
            'order': self.kwargs['pk'],
            'warehouse': warehouse.pk
        }

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        data = json.loads(urllib.parse.unquote(request.POST['received-items']))
        subtotal = D(0)
        for line in data:
            pk = line['item'].split("-")[0]
            n = line['quantity_received']
            if n == 0:
                continue

            item = models.OrderItem.objects.get(pk=pk)

            if line['receiving_location'] != "":
                medium = line['receiving_location'].split('-')[0]
                item.receive(n, medium=medium, receipt=self.object)
            else:
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

class OrderGoodsReceiptsList(TemplateView):
    template_name=os.path.join('inventory','goods_received', 'list.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = models.Order.objects.get(
            pk=self.kwargs['pk'])

        return context 
    

#################################################
#                  Transfers                    #
#################################################


class IncomingTransferOrderListView(ContextMixin, PaginationMixin, FilterView):
    filterset_class = filters.IncomingTransferOrderFilter
    template_name = os.path.join('inventory', 'incoming','transfer', 'list.html')
    paginate_by = 20
    extra_context = {
        'title': 'List of Incoming Transfer Orders',
        
    }
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['warehouse'] = int(self.kwargs['pk'])
        
        return context

    def get_queryset(self):
        warehouse = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return models.TransferOrder.objects.filter(Q(
            receiving_warehouse=warehouse)).order_by('date').reverse()


class TransferOrderReceiveView(ContextMixin, CreateView):
    template_name = os.path.join('inventory', 'incoming', 'transfer', 'create.html')
    form_class = forms.IncomingTransferStockReceiptForm
    model = models.StockReceipt
    extra_context = {
        'title': 'Receive Transfer of Inventory'
    }

    def get_initial(self):
        return {
            'transfer': self.kwargs['pk'],
            'warehouse': self.kwargs['warehouse']
        }


    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp

        for item in json.loads(urllib.parse.unquote(
                request.POST['received-items'])):
            line = models.TransferOrderLine.objects.get(
                pk=item['item'].split('-')[0])
            location = None
            if item["receiving_location"] != "":
                location = item["receiving_location"].split("-")[0]
            quantity = float(item['quantity_to_move'])
            models.StockReceiptLine.objects.create(
                    transfer_line = line,
                    quantity=quantity,
                    location = location,
                    receipt=self.object
                )
            #dispatch is concerned with decrementing inventory
            line.transfer_order.receiving_warehouse.add_item(
                line.item, quantity, location=location
            )

        return resp

class TransferOrderReceiptsList(TemplateView):
    template_name=os.path.join('inventory','incoming', 'transfer', 'detail_list.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        transfer =models.TransferOrder.objects.get(
            pk=self.kwargs['pk'])
        context['transfer'] = transfer
        context['warehouse'] = transfer.receiving_warehouse.pk

        return context 


#################################################
#                  Credit Notes                 #
#################################################

class CreditNoteStockReceiptCreateView(CreateView):
    form_class = forms.SalesReturnStockReceiptForm
    model = models.StockReceipt
    template_name = os.path.join("inventory", "incoming",
        "credit_note", "create.html")

    def get_initial(self):
        note = CreditNote.objects.get(pk=self.kwargs['pk'])

        return {
            'credit_note': self.kwargs['pk'],
            'warehouse': note.invoice.ship_from.pk
        }

    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        if not self.object:
            return resp
        
        note = CreditNote.objects.get(pk=self.kwargs['pk'])
        warehouse = note.invoice.ship_from
        data = json.loads(urllib.parse.unquote(request.POST['received-items']))
        subtotal = D(0)
        for line in data:
            note_line = CreditNoteLine.objects.get(pk=line['id'])

            pk = line['item'].split("-")[0]
            item = models.InventoryItem.objects.get(pk=pk)
            n = line['quantity']
            if n == 0:
                continue

            medium = None
            if line['receiving_location'] != "":
                medium_id = line['receiving_location'].split('-')[0]
                medium = models.StorageMedia.objects.get(pk=medium_id)
                warehouse.add_item(item, n, location=medium)
            else:
                warehouse.add_item(item, n)

            models.StockReceiptLine.objects.create(
                    credit_note_line = note_line,
                    quantity=n,
                    location = medium,
                    receipt=self.object
                )
        
        return resp


class IncomingReturnsListView(ContextMixin, PaginationMixin, FilterView):
    model = CreditNote
    template_name= os.path.join('inventory', 'incoming', 'credit_note', 
        'list.html')
    filterset_class = filters.IncomingCreditNoteFilters
    extra_context = {
        'title': 'List Of Credit Notes with Returns'
    }


    def get_queryset(self):
        warehouse = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return CreditNote.objects.filter(invoice__ship_from=warehouse)    


class SingleSalesReturnListView(TemplateView):
    template_name = os.path.join('inventory', 'incoming', 'credit_note', 'detail_list.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['note'] = CreditNote.objects.get(pk=self.kwargs['pk'])
        return context
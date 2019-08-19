
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


class TransferOrderCreateView(CreateView):
    '''
    Page for moving inventory between warehouses.
    Currently only supports products.
    '''
    template_name = os.path.join('inventory', 'transfer', 'create.html')
    form_class = forms.TransferOrderForm

    def get_initial(self):
        return {
            'source_warehouse': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        resp = super(TransferOrderCreateView, self).post(
            request, *args, **kwargs)
        if not self.object:
            return resp 
        
        data = json.loads(urllib.parse.unquote(request.POST['items'])) 
        for i in data:
            pk, _ = i['item'].split('-')[0]
            item = models.InventoryItem.objects.get(pk=pk)
            wh_item = self.object.source_warehouse.get_item(item)
            print(wh_item)
            if wh_item and wh_item.quantity >= float(i['quantity']):
                models.TransferOrderLine.objects.create(
                    item = item,
                    quantity = i['quantity'],
                    transfer_order = self.object
                )
            else:
                messages.info(request, 'The selected source warehouse has insufficient quantity of item %s to make the transfer' % item)
        return resp



class OutgoingTransferOrderListView(ContextMixin, PaginationMixin, FilterView):
    filterset_class = filters.OutgoingTransferOrderFilter
    template_name = os.path.join('inventory', 'transfer', 'list.html')
    paginate_by = 20
    extra_context = {
        'title': 'List of Outgoing Transfer Orders',
        
    }
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['warehouse'] = int(self.kwargs['pk'])
        context['new_link'] = '/inventory/create-transfer-order/' + \
            self.kwargs['pk']
        return context

    def get_queryset(self):
        warehouse = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return models.TransferOrder.objects.filter(
            Q(source_warehouse=warehouse)).order_by('date').reverse()


class TransferOrderDetailView(ContextMixin, 
                              ConfigMixin,
                              MultiPageDocument, 
                              DetailView):
    model = models.TransferOrder
    template_name = os.path.join('inventory', 'transfer', 'document.html')
    extra_context = {
        'pdf_link': True
    }
    paginate_by =20

    def get_multipage_queryset(self):
        return self.object.transferorderline_set.all()

class TransferOrderAPIView(RetrieveAPIView):
    serializer_class = serializers.TransferOrderSerializer 
    queryset = models.TransferOrder.objects.all()
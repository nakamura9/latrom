# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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


#######################################################
#               Inventory Check Views                 #
#######################################################

CREATE_TEMPLATE = os.path.join("common_data", "create_template.html")

class InventoryCheckCreateView(CreateView):
    '''
    Also Known as stock take. Used to compare actual inventory versus recorded inventory. Each item in a warehouse is examined and verified. 
    Changes are made to each warehouse based on data recorded here.
    '''
    template_name = os.path.join('inventory', 'inventory_check', 'create.html')
    form_class = forms.InventoryCheckForm
    success_url = reverse_lazy('inventory:warehouse-list') 
    
    def get_initial(self):
        return {
            'warehouse': self.kwargs['pk']
        }

    def post(self, request, *args, **kwargs):
        resp = super(InventoryCheckCreateView, self).post(
            request, *args, **kwargs)
        if not self.object:
            return resp
        
        raw_data = request.POST['check-table']
        adjustments = json.loads(urllib.parse.unquote(raw_data))
        for adj in adjustments:
            pk = adj['item'].split('-')[0]
            delta = float(adj['quantity']) - float(adj['measured'])
            if delta != 0:
                wh_item = models.WareHouseItem.objects.get(pk=pk)
                models.StockAdjustment.objects.create(
                    warehouse_item = wh_item,
                    inventory_check = self.object,
                    note = "",# could add note widget
                    adjustment = delta
                )

        return resp


class InventoryCheckDetailView(DetailView):
    model = models.InventoryCheck
    template_name = os.path.join('inventory', 'inventory_check', 'summary.html')

class InventoryCheckListView(ContextMixin ,PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryCheckFilter
    template_name = os.path.join("inventory", "inventory_check", 'list.html')
    extra_context = {
        "title": "List of Inventory Checks",
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['new_link'] = reverse_lazy('inventory:create-inventory-check')
        return context
    def get_queryset(self):
        w = models.WareHouse.objects.get(pk=self.kwargs['pk'])
        return models.InventoryCheck.objects.filter(
            warehouse=w).order_by('date').reverse()


class StockAdjustmentAPIView(ModelViewSet):
    queryset = models.StockAdjustment.objects.all()
    serializer_class = serializers.StockAdjustmentSerializer


class DebitNoteAPIView(ModelViewSet):
    queryset = models.DebitNote.objects.all()
    serializer_class = serializers.DebitNoteSerializer

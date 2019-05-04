# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
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
from common_data.views import PaginationMixin
from inventory import filters, forms, models, serializers
from invoicing.models import SalesConfig
from services.models import EquipmentRequisition

from .common import CREATE_TEMPLATE

class ItemSelectionPage(TemplateView):
    template_name = os.path.join('inventory', 'item', 'selection.html')

class InventoryItemAPIView(ModelViewSet):
    queryset = models.InventoryItem.objects.all()
    serializer_class = serializers.InventoryItemSerializer


class InventoryItemDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.InventoryItem
    success_url = reverse_lazy('inventory:product-list')


class InventoryItemDetailView( DetailView):
    model = models.InventoryItem
    template_name = os.path.join("inventory", "item", "product", "detail.html")


class InventoryItemListView( ContextMixin, PaginationMixin, FilterView):
    paginate_by = 20
    filterset_class = filters.InventoryItemFilter
    template_name = os.path.join('inventory', 'item', "product", 'list.html')
    extra_context = {
        'title': 'InventoryItem List',
        "new_link": reverse_lazy("inventory:product-create")
    }

    def get_queryset(self):
        return models.InventoryItem.objects.all().order_by('pk')

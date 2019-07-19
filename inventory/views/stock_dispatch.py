
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


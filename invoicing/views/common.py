# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib
import datetime

from django.conf import settings
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, FormView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from rest_framework import generics, viewsets

from accounting.forms import TaxForm
from common_data.utilities import ContextMixin, ConfigMixin
from invoicing import filters, forms, serializers
from invoicing.models import *


class SalesConfigMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        return context

class Home(SalesConfigMixin, TemplateView):
    template_name = os.path.join("invoicing", "dashboard.html")

    def get_context_data(self, **kwargs):
        TODAY =datetime.date.today()

        context = super().get_context_data(**kwargs)
        first = TODAY - datetime.timedelta(days=TODAY.day)
        context['sales_to_date'] = sum([i.total for i in \
             SalesInvoice.objects.filter(status="invoice", date__gt=first )])
        context['customers'] = Customer.objects.filter(active=True).count()
        context['outstanding_invoices'] = SalesInvoice.objects.filter(Q(
            status="invoice") | Q(status="paid-partially")).count()
        
        context['money_owed'] = sum([i.total_due for i in \
            SalesInvoice.objects.filter(Q(status="invoice") | Q(
                status="paid-partially"))])

        context['overdue'] = SalesInvoice.objects.filter(Q(Q(
            status="invoice") | Q(status="paid-partially")) & Q(
                due__gt=TODAY
            )).count()

        return context
        

#########################################################
#                  Template Views                       #
#########################################################


class ConfigView( UpdateView):
    template_name = os.path.join("invoicing", "config.html")
    form_class = forms.SalesConfigForm
    model = SalesConfig
    success_url = reverse_lazy('invoicing:home')
    
    
class ConfigAPIView(generics.RetrieveAPIView):
    queryset = SalesConfig.objects.all()
    serializer_class = serializers.ConfigSerializer


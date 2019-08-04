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
from common_data.utilities import ContextMixin, ConfigMixin, ConfigWizardBase
from invoicing import filters, forms, serializers
from invoicing.models import *
from invoicing.views.report_utils import plotters
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from employees.models import Employee
from employees.forms import EmployeeForm

class SalesConfigMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(SalesConfig.objects.first().__dict__)
        return context

class Home(SalesConfigMixin, TemplateView):
    template_name = os.path.join("invoicing", "dashboard.html")

    def get(self, *args, **kwargs):
        if SalesConfig.objects.first().is_configured:
            return super().get(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy('invoicing:config-wizard'))

class AsyncDashboard(TemplateView):
    template_name = os.path.join('invoicing', 'async_dashboard.html')

    def get_context_data(self, **kwargs):
        TODAY =datetime.date.today()

        context = super().get_context_data(**kwargs)
        first = TODAY - datetime.timedelta(days=TODAY.day)
        context['sales_to_date'] = sum([i.total for i in \
             Invoice.objects.filter(status="invoice", date__gt=first )])
        context['customers'] = Customer.objects.filter(active=True).count()
        context['outstanding_invoices'] = Invoice.objects.filter(Q(
            status="invoice") | Q(status="paid-partially")).count()
        
        context['money_owed'] = sum([i.total_due for i in \
            Invoice.objects.filter(Q(status="invoice") | Q(
                status="paid-partially"))])

        context['overdue'] = Invoice.objects.filter(Q(Q(
            status="invoice") | Q(status="paid-partially")) & Q(
                due__gt=TODAY
            )).count()

        context['graph'] = plotters.plot_sales(
            datetime.date.today() - datetime.timedelta(days=30),
            datetime.date.today()
        )
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

def employee_condition(self):
    return Employee.objects.all().count() == 0

class ConfigWizard(ConfigWizardBase):
    template_name = os.path.join('invoicing', 'wizard.html')
    form_list = [
        forms.SalesConfigForm, 
        forms.CustomerForm, 
        EmployeeForm,
        forms.SalesRepForm
    ]

    condition_dict = {
        '2' : employee_condition
    }

    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'logo'))

    config_class = SalesConfig
    success_url = reverse_lazy('invoicing:home')

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if step == '1':
            initial.update({'customer_type': 'individual'})

        return initial

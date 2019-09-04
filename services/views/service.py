# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from rest_framework import viewsets

from common_data.utilities import ContextMixin, ConfigWizardBase
from common_data.views import PaginationMixin
from services import filters, forms, models, serializers
from formtools.wizard.views import SessionWizardView
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from employees.forms import EmployeeForm
from employees.models import Employee
import urllib
import json




CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')
#####################################################
#                   Service Views                   #
#####################################################

class ServiceCreateView( ContextMixin, CreateView):
    form_class = forms.ServiceForm
    template_name = os.path.join('common_data','crispy_create_template.html')
    success_url = reverse_lazy('services:dashboard')
    extra_context = {
        'title': 'Create Service',
        'description': 'Make service listings, including features like the procedure, cost and frequency.',
        'related_links': [{
            'name': 'Create Procedure',
            'url': '/services/create-procedure'
        },{
            'name': 'Create Service Category',
            'url': '/services/create-category/'
        }],
        'box_array': urllib.parse.quote(json.dumps(
            [{
                'model': 'serviceprocedure',
                'app': 'services',
                'id': 'id_procedure'
            },
            {
                'model': 'servicecategory',
                'app': 'services',
                'id': 'id_category'
            }
            ]))
    }

    def get_initial(self):
        return {
            'frequency': 'once',
            'hourly_rate': 0.0,
            'flat_fee': 0.0
        }

class ServiceUpdateView( ContextMixin, UpdateView):
    form_class = forms.ServiceForm
    model = models.Service
    template_name = os.path.join('common_data','crispy_create_template.html')
    success_url = reverse_lazy('services:dashboard')
    extra_context = {
        'title': 'Update Service',
        'description': 'Make service listings, including features like the procedure, cost and frequency.',
        'related_links': [{
            'name': 'Create Procedure',
            'url': '/services/create-procedure'
        },{
            'name': 'Create Service Category',
            'url': '/services/create-category/'
        }],
        'box_array': urllib.parse.quote(json.dumps(
            [{
                'model': 'serviceprocedure',
                'app': 'services',
                'id': 'id_procedure'
            },
            {
                'model': 'servicecategory',
                'app': 'services',
                'id': 'id_category'
            }
            ]))
    }

class ServiceListView( ContextMixin, PaginationMixin, FilterView):
    filterset_class = filters.ServiceFilter
    model = models.Service
    template_name = os.path.join('services', 'service', 'list.html')
    extra_context = {
        'title': 'List of offered services',
        'new_link': reverse_lazy('services:create-service')
    }
    
class ServiceDetailView( DetailView):
    template_name = os.path.join('services', 'service', 'detail.html')
    model = models.Service 

class ServiceAPIView(viewsets.ModelViewSet):
    queryset = models.Service.objects.all()
    serializer_class = serializers.ServiceSerializer

def employee_condition(self):
    return Employee.objects.all().count() == 0

class ConfigWizard(ConfigWizardBase):
    template_name = os.path.join('services', 'wizard.html')
    form_list = [
        forms.ServiceForm, 
        EmployeeForm,
        forms.ServicePersonForm
    ]

    condition_dict = {
        '1': employee_condition
    }

    config_class = models.ServicesSettings
    success_url = reverse_lazy('services:dashboard')
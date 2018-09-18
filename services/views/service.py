# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os


from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView
from services import forms 
from services import models
from services import filters
from common_data.utilities import ExtraContext
from django_filters.views import FilterView
from common_data.views import PaginationMixin

from rest_framework import viewsets

from services import serializers

class Dashboard(TemplateView):
    template_name = os.path.join('services', 'dashboard.html')


CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')
#####################################################
#                   Service Views                   #
#####################################################

class ServiceCreateView(ExtraContext, CreateView):
    form_class = forms.ServiceForm
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy('services:dashboard')
    extra_context = {
        'title': 'Create new service Listing'
    }

class ServiceUpdateView(ExtraContext, UpdateView):
    form_class = forms.ServiceForm
    model = models.Service
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy('services:dashboard')
    extra_context = {
        'title': 'Update existing service Listing'
    }

class ServiceListView(ExtraContext, PaginationMixin, FilterView):
    filterset_class = filters.ServiceFilter
    model = models.Service
    template_name = os.path.join('services', 'service', 'list.html')
    extra_context = {
        'title': 'List of offered services',
        'new_link': reverse_lazy('services:create-service')
    }
    
class ServiceDetailView(DetailView):
    template_name = os.path.join('services', 'service', 'detail.html')
    model = models.Service 

class ServiceAPIView(viewsets.ModelViewSet):
    queryset = models.Service.objects.all()
    serializer_class = serializers.ServiceSerializer

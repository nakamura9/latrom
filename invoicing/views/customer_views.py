# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView
from rest_framework import viewsets

from common_data.utilities import ExtraContext
from common_data.views import PaginationMixin
from invoicing import filters, forms, serializers
from invoicing.models import Customer

from .common import SalesRepCheckMixin

#########################################
#           Customer Views              #
#########################################

class CustomerAPIViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer

#No customer list, overlooked!

class CustomerCreateView(SalesRepCheckMixin, ExtraContext, CreateView):
    extra_context = {
        "title": "New Customer",
        'description': 'Register new customers which may be organizational or private individuals. ',
        'related_links': [{
            'name': 'Create Organizational Customer',
            'url': '/base/organization/create'
        },{
            'name': 'Record Individual Customer',
            'url': '/base/individual/create'
        }]}
    template_name = os.path.join("common_data", "create_template.html")
    model = Customer
    success_url = reverse_lazy("invoicing:home")
    form_class = forms.CustomerForm


class CustomerUpdateView(SalesRepCheckMixin, ExtraContext, UpdateView):
    extra_context = {"title": "Update Existing Customer"}
    template_name = os.path.join("common_data", "create_template.html")
    model = Customer
    form_class = forms.CustomerForm
    success_url = reverse_lazy("invoicing:home")


class CustomerListView(SalesRepCheckMixin, ExtraContext, PaginationMixin, FilterView):
    extra_context = {"title": "List of Customers",
                    "new_link": reverse_lazy("invoicing:create-customer")}
    template_name = os.path.join("invoicing", "customer_list.html")
    filterset_class = filters.CustomerFilter
    paginate_by = 10

    def get_queryset(self):
        return Customer.objects.all().order_by('pk')


class CustomerDeleteView(SalesRepCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = Customer
    success_url = reverse_lazy('invoicing:customers-list')

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, DetailView, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from django_filters.views import FilterView
from django.urls import reverse_lazy
from invoicing import forms

from common_data.utilities import ExtraContext, apply_style
from invoicing.models import *
from invoicing import filters
from invoicing import serializers
from views import SalesRepCheckMixin

#########################################
#               Payment Views           #
#########################################


class PaymentAPIViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = serializers.PaymentsSerializer

class PaymentDeleteView(SalesRepCheckMixin, DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = Payment
    success_url = reverse_lazy("invoicing:invoices-list")

class PaymentCreateView(SalesRepCheckMixin, ExtraContext, CreateView):
    extra_context = {"title": "Create New Payment"}
    template_name = os.path.join("common_data", "create_template.html")
    model = Payment
    success_url = reverse_lazy("invoicing:home")
    form_class = forms.PaymentForm

class PaymentUpdateView(SalesRepCheckMixin, ExtraContext, UpdateView):
    extra_context = {"title": "Update Existing Payment"}
    template_name = os.path.join("common_data", "create_template.html")
    model = Payment
    form_class = forms.PaymentUpdateForm #some fields missing!
    success_url = reverse_lazy("invoicing:home")

class SalesRepDeleteView(SalesRepCheckMixin, DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = SalesRepresentative
    success_url = reverse_lazy("invoicing:invoices-list")

class PaymentListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "List of Payments",
                    "new_link": reverse_lazy("invoicing:create-payment")}
    template_name = os.path.join("invoicing", "payment_list.html")
    filterset_class = filters.PaymentFilter
    paginate_by = 10
    
    def get_queryset(self):
        return Payment.objects.all().order_by('date')


# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from rest_framework import viewsets
from django_filters.views import FilterView
from django.urls import reverse_lazy, reverse
from invoicing import forms

from common_data.utilities import ExtraContext
from invoicing.models import SalesRepresentative
from invoicing import filters
from invoicing import serializers
from common import SalesRepCheckMixin

#########################################
#           Sales Rep Views             #
#########################################

class SalesRepCreateView(SalesRepCheckMixin, ExtraContext, CreateView):
    extra_context = {"title": "Add New Sales Rep."}
    template_name = os.path.join("common_data", "create_template.html")
    model = SalesRepresentative
    success_url = reverse_lazy("invoicing:home")
    form_class = forms.SalesRepForm


class SalesRepUpdateView(SalesRepCheckMixin,ExtraContext, UpdateView):
    extra_context = {"title": "Update Existing Sales Rep."}
    template_name = os.path.join("common_data", "create_template.html")
    model = SalesRepresentative
    form_class = forms.SalesRepForm
    success_url = reverse_lazy("invoicing:home")


class SalesRepListView(SalesRepCheckMixin, ExtraContext, FilterView):
    extra_context = {"title": "List of Sales Representatives",
                    "new_link": reverse_lazy("invoicing:create-sales-rep")}
    template_name = os.path.join("invoicing", "sales_rep_list.html")
    filterset_class = filters.SalesRepFilter
    paginate_by = 10

    def get_queryset(self):
        return SalesRepresentative.objects.all().order_by('pk')

class SalesRepsAPIViewSet(viewsets.ModelViewSet):
    queryset = SalesRepresentative.objects.all()
    serializer_class = serializers.SalesRepsSerializer

class SalesRepDeleteView(SalesRepCheckMixin, DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = SalesRepresentative
    success_url = reverse_lazy("invoicing:invoices-list")
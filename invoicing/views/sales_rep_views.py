# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView
from rest_framework import viewsets

from common_data.utilities import ContextMixin
from common_data.views import PaginationMixin
from invoicing import filters, forms, serializers
from invoicing.models import SalesRepresentative


#########################################
#           Sales Rep Views             #
#########################################

class SalesRepCreateView( ContextMixin, CreateView):
    extra_context = {"title": "Add New Sales Rep."}
    template_name = os.path.join("common_data", "create_template.html")
    model = SalesRepresentative
    success_url = reverse_lazy("invoicing:home")
    form_class = forms.SalesRepForm


class SalesRepUpdateView(ContextMixin, UpdateView):
    extra_context = {"title": "Update Existing Sales Rep."}
    template_name = os.path.join("common_data", "create_template.html")
    model = SalesRepresentative
    form_class = forms.SalesRepForm
    success_url = reverse_lazy("invoicing:home")


class SalesRepListView( ContextMixin, PaginationMixin, FilterView):
    extra_context = {"title": "List of Sales Representatives",
                    "new_link": reverse_lazy("invoicing:create-sales-rep")}
    template_name = os.path.join("invoicing", "sales_rep_list.html")
    filterset_class = filters.SalesRepFilter
    paginate_by = 20

    def get_queryset(self):
        return SalesRepresentative.objects.all().order_by('pk')

class SalesRepsAPIViewSet(viewsets.ModelViewSet):
    queryset = SalesRepresentative.objects.all()
    serializer_class = serializers.SalesRepsSerializer

class SalesRepDeleteView( DeleteView):
    template_name = os.path.join("common_data", "delete_template.html")
    model = SalesRepresentative
    success_url = reverse_lazy("invoicing:sales-reps-list")

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from rest_framework import generics, viewsets
from django_filters.views import FilterView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.conf import settings
from invoicing import forms

from common_data.utilities import ExtraContext, apply_style, Modal
from inventory.forms import QuickProductForm
from accounting.forms import TaxForm
from inventory.models import Product
from invoicing.models import *
from invoicing import filters
from invoicing import serializers


class SalesRepCheckMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        elif hasattr(self.request.user, 'employee') and \
                self.request.user.employee.is_sales_rep:
            return True
        else:
            return False

class Home(SalesRepCheckMixin, TemplateView):
    template_name = os.path.join("invoicing", "home.html")

        

#########################################################
#                  Template Views                       #
#########################################################


class ConfigView(SalesRepCheckMixin, UpdateView):
    template_name = os.path.join("invoicing", "config.html")
    form_class = forms.SalesConfigForm
    model = SalesConfig
    success_url = reverse_lazy('invoicing:home')
    
    
class ConfigAPIView(generics.RetrieveAPIView):
    queryset = SalesConfig.objects.all()
    serializer_class = serializers.ConfigSerializer

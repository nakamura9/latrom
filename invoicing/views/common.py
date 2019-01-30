# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.conf import settings
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
from inventory.forms import QuickProductForm
from inventory.models import Product
from invoicing import filters, forms, serializers
from invoicing.models import *



class Home( ConfigMixin, TemplateView):
    template_name = os.path.join("invoicing", "dashboard.html")

        

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


# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib

from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from invoicing import forms

from common_data.utilities import ExtraContext, apply_style
from inventory.models import Product
from invoicing.models import *
from invoicing import filters
from invoicing import serializers
from views import SalesRepCheckMixin

################################################
#                   Sales Invoice              #
################################################




########################################################
#                   Bill Views                         #
########################################################




########################################################
#                   Service Invoice                    #
########################################################


########################################################
#                   Combined Invoice                    #
########################################################

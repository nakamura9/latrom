# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import urllib

from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from common_data.utilities import ExtraContext, apply_style
from inventory.models import Product
from invoicing import filters, forms, serializers
from invoicing.models import *
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

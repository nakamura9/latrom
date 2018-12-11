from manufacturing.views.process import *
from manufacturing.views.shift import *
from manufacturing.views.equipment import *
import os

from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect
from manufacturing.views.util import ManufacturingCheckMixin

class Dashboard(ManufacturingCheckMixin, TemplateView):
    template_name = os.path.join('manufacturing', 'dashboard.html')
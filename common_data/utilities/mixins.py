import datetime
import json
import os

from django.urls import re_path
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from common_data import models 
import invoicing
from latrom import settings
from .functions import apply_style, PeriodSelectionException

class ConfigMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        config = models.GlobalConfig.objects.first()
        context.update(config.__dict__)
        context.update({
            'logo': config.logo,
            'logo_width': config.logo_width,
            'business_name': config.business_name,
            'business_address': config.business_address
        })
        return apply_style(context)


class ContextMixin(object):
    extra_context = {}
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update(self.extra_context)
        return context


class PeriodReportMixin(View):
    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except PeriodSelectionException as e:
            return HttpResponse(f'<h3>{e}</h3>')
import datetime
import json
import os

from django.urls import re_path
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from common_data import models 
import invoicing
from latrom import settings
from .functions import apply_style


class ConfigMixin(object):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        config = models.GlobalConfig.objects.first()
        context.update(config.__dict__)
        
        context.update({
            'logo': config.logo,
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



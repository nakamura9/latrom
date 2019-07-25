import datetime
import json
import os

from django.urls import re_path
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, View
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from common_data import models
import messaging
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


class ContactsMixin(object):
    '''Contacts mixin is a utility class used to extract email addresses and phone numbers from text fields in places where it is inconvenient to rename a foreign key'''
    email_fields = []
    phone_fields = []

    def save(self, *args, **kwargs):
        ret = super().save(*args, **kwargs)
        for field in self.email_fields:
            address = self.__getattribute__(field)
            if address and address != "":
                if not messaging.models.EmailAddress.objects.filter(
                        address=address).exists():
                    messaging.models.EmailAddress.objects.create(
                        address=address)

        for field in self.phone_fields:
            number = self.__getattribute__(field)
            if number and number != "":
                if not models.PhoneNumber.objects.filter(number=number).exists():
                    models.PhoneNumber.objects.create(number=number)

        return ret


class AutomatedServiceMixin(object):
    '''
    Ensures the service is only run once per day. Especially for servers 
    that restart multiple times a day
    '''
    def run(self):
        config = models.GlobalConfig.objects.first()
        if config.last_automated_service_run and \
                (config.last_automated_service_run - \
                    datetime.datetime.now()).total_seconds() > 86400:
            self._run()
        print('service has already run for today')    
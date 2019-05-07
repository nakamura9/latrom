import datetime
from decimal import Decimal as D
import os
from functools import reduce
import urllib
from itertools import chain

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect

from common_data.forms import PeriodReportForm
from common_data.utilities import (ContextMixin, 
                                    extract_period, 
                                    PeriodReportMixin,
                                    ConfigMixin)
from invoicing import models as inv
from inventory import models as inventory_models
from wkhtmltopdf.views import PDFTemplateView
from accounting import forms, models

from django.test import Client
import csv

class AccountReportFormView(ContextMixin, FormView):
    form_class = forms.AccountReportForm
    template_name = os.path.join('common_data', 'reports', 'report_template.html')
    
    extra_context = {
        'action': reverse_lazy('accounting:account-report'),
    }

    def get_initial(self):
        return {
            'account': self.kwargs['pk']
        }

class AccountReport(ConfigMixin, PeriodReportMixin, TemplateView):
    template_name = os.path.join('accounting', 'reports', 
        'account.html')

    @staticmethod
    def common_context(context, start, end):
        account = models.Account.objects.get(pk=context['account'])
        debits = models.Debit.objects.filter(account=account, 
                                        entry__date__gte=start, 
                                        entry__date__lte=end)
        credits = models.Credit.objects.filter(account=account, 
                                        entry__date__gte=start, 
                                        entry__date__lte=end)
        
        context['object_list'] = sorted(chain(debits,credits), 
            key=lambda transaction: transaction.entry.date)

        context.update({
            'account': account,
            'start': start.strftime("%d %B %Y"),
            'end': end.strftime("%d %B %Y")
        })
        
        return context


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        kwargs =  self.request.GET
        start, end = extract_period(kwargs)
        
        context['pdf_link'] = True
        context['account'] = kwargs['account']
        # sales
        return AccountReport.common_context(context, start, end)

class AccountReportPDFView(ConfigMixin, PDFTemplateView):
    template_name = AccountReport.template_name

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['account'] = self.kwargs['account']

        start = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['start']), "%d %B %Y")
        end = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['end']), "%d %B %Y")
        return AccountReport.common_context(context, start, end)
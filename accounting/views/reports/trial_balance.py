import datetime
from decimal import Decimal as D
import os
from functools import reduce

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView

from common_data.forms import PeriodReportForm
from common_data.utilities import (ContextMixin,  
                                    ConfigMixin,
                                    MultiPageDocument) 
from invoicing import models as inv
from inventory import models as inventory_models
from wkhtmltopdf.views import PDFTemplateView

from accounting import forms, models


class TrialBalance(ConfigMixin, MultiPageDocument, TemplateView):
    template_name = os.path.join('accounting', 'reports', 'trial_balance', 'report.html')

    page_length=20

    def get_multipage_queryset(self):
        return models.Account.objects.all().exclude(
            Q(balance=0.0) & Q(control_account=False)).exclude(
                parent_account__isnull=False).order_by('pk')

    @staticmethod
    def common_context(context):
        context['date'] = datetime.date.today()
        context['accounts'] = models.Account.objects.all().exclude(
            Q(balance=0.0) & Q(control_account=False)).exclude(
                parent_account__isnull=False).order_by('pk')

        context['total_debit'] = models.Account.total_debit()
        context['total_credit'] = models.Account.total_credit()
        context["inventory_value"] = inventory_models.InventoryItem.total_inventory_value()
        
        return context

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['pdf_link'] = True

        return TrialBalance.common_context(context)

class TrialBalancePDFView(ConfigMixin, MultiPageDocument, PDFTemplateView):
    template_name = TrialBalance.template_name
    page_length=20

    def get_multipage_queryset(self):
        return models.Account.objects.all().exclude(
            Q(balance=0.0) & Q(control_account=False)).exclude(
                parent_account__isnull=False).order_by('pk')
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return TrialBalance.common_context(context)
        
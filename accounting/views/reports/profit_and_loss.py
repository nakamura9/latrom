import datetime
from decimal import Decimal as D
import os
from functools import reduce
import urllib

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView
from django.http import HttpResponseRedirect

from common_data.forms import PeriodReportForm
from common_data.utilities import ContextMixin, extract_period, PeriodReportMixin, ConfigMixin
from invoicing import models as inv
from inventory import models as inventory_models
from wkhtmltopdf.views import PDFTemplateView
from accounting import forms, models

from django.test import Client
from bs4 import BeautifulSoup
import csv

class ProfitAndLossFormView(ContextMixin, FormView):
    form_class = PeriodReportForm
    template_name = os.path.join('common_data', 'reports', 'report_template.html')
    
    extra_context = {
        'action': reverse_lazy('accounting:profit-and-loss'),
    }

class ProfitAndLossReport(ConfigMixin, PeriodReportMixin, TemplateView):
    template_name = os.path.join('accounting', 'reports', 
        'profit_and_loss', 'report.html')

    @staticmethod
    def common_context(context, start, end):
        sales_acc = models.Account.objects.get(pk=4000)
        sales_balance_carried_over = sales_acc.balance_on_date(start)
        sales = sales_acc.balance - sales_balance_carried_over
        
        #purchases
        # TODO verify if opening inventory is considered in profit and loss statement

        purchases_acc = models.Account.objects.get(pk=4006)
        purchase_returns_acc = models.Account.objects.get(pk=4008)
        purchase_returns = purchase_returns_acc.balance_over_period(start, end)
        purchases = purchases_acc.balance_over_period(start, end) + purchase_returns
        
        opening_inventory = sum(
            [D(i.quantity_on_date(start)) * i.unit_value for i in inventory_models.InventoryItem.objects.filter(product_component__isnull=False)])
        print(opening_inventory)
        
        closing_inventory = inventory_models.InventoryItem.total_inventory_value()
        cogs = opening_inventory +  purchases - closing_inventory
        #cost of revenue
        # calculate direct labour for services
        # include commissions in cost of goods sold

        other_income = models.Account.objects.filter(type="income").exclude(
            Q(balance=0.0)).exclude(Q(pk__in=[4000]))

        other_income_total = sum([i.control_balance for i in other_income])

        total_gross_profit = sales - cogs + other_income_total


        expenses = models.Account.objects.filter(
            type="expense").exclude(
                Q(balance=0.0))

        total_expenses = sum([i.control_balance for i in expenses])

        context.update({
            'start': start.strftime("%d %B %Y"),
            'end': end.strftime("%d %B %Y"),
            'sales': sales,
            'purchases': purchases,
            'closing_inventory': closing_inventory,
            'opening_inventory': opening_inventory,
            'cost_of_goods_sold': cogs,
            'gross_profit': sales - cogs,
            'other_income_accounts': other_income,
            'other_income_total': other_income_total,
            'total_revenue': total_gross_profit,
            'expenses': expenses,
            'total_expenses': total_expenses,
            'net_profit': total_gross_profit - total_expenses
        })
        
        return context


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        kwargs =  self.request.GET
        start, end = extract_period(kwargs)
        context['pdf_link'] = True
        # sales
        return ProfitAndLossReport.common_context(context, start, end)

class ProfitAndLossReportPDFView(ConfigMixin, PDFTemplateView):
    template_name = ProfitAndLossReport.template_name

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        start = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['start']), "%d %B %Y")
        end = datetime.datetime.strptime(urllib.parse.unquote(
            self.kwargs['end']), "%d %B %Y")
        return ProfitAndLossReport.common_context(context, start, end)
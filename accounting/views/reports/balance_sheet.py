import datetime
from decimal import Decimal as D
import os
from functools import reduce

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView

from common_data.forms import PeriodReportForm
from common_data.utilities import ContextMixin, ConfigMixin
from invoicing import models as inv
from inventory import models as inventory_models
from .util import net_profit_calculator
from wkhtmltopdf.views import PDFTemplateView

from accounting import forms, models
'''Note: Recorded carriage and other costs of goods sold as current assets'''

class BalanceSheet(ConfigMixin,TemplateView):
    template_name = os.path.join('accounting', 'reports', 'balance_sheet','report.html')


    @staticmethod
    def common_context(context):
        delta_mapping = {
            0: 365,
            1: 30,
            2: 7
        }

        end = datetime.date.today()

        start = end - datetime.timedelta(days=delta_mapping[
            models.AccountingSettings.objects.first().default_accounting_period
        ])

        #LONG TERM ASSETS
        long_term_assets = models.Account.objects.filter(
            Q(balance_sheet_category='non-current-assets')).exclude(
                Q(balance=0) & Q(control_account=False))

        long_term_assets_total = sum(
            [i.balance for i in long_term_assets]
        )


        #CURRENT ASSETS 
        current_assets = models.Account.objects.filter(
            Q(balance_sheet_category='current-assets') ).exclude(
                Q(
                    Q(balance=0)  & Q(control_account=False)
                    ) | 
                Q(parent_account=models.Account.objects.get(pk=1003)))


        inventory = inventory_models.InventoryItem.total_inventory_value()
        current_assets_total = sum(
            [i.control_balance for i in current_assets] 
        ) + inventory

        #CURRENT LIABILITIES
        current_liabilities = models.Account.objects.filter(
            Q(balance_sheet_category='current-liabilities')).exclude(
                Q(
                    Q(balance=0) & Q(control_account=False)
                    ) |
                Q(parent_account=models.Account.objects.get(pk=2000)))

        
        current_liabilities_total = sum(
            [i.control_balance for i in current_liabilities]
        )

        working_capital =  current_assets_total - current_liabilities_total
        
        #LONG TERM LIABILITIES
        long_term_liabilities = models.Account.objects.filter(
            Q(balance_sheet_category='non-current-liabilities')).exclude(
                Q(balance=0))

        long_term_liabilities_total = sum(
            [i.balance for i in long_term_liabilities]
        )

        net_assets = long_term_assets_total + working_capital - \
            long_term_liabilities_total

        #EQUITY
        equity = models.Account.objects.filter(type='equity').exclude(
                Q(balance=0) | Q(pk=3003)
            )

        drawings = models.Account.objects.get(pk=3003).control_balance

        net_profit = net_profit_calculator(start, end)

        equity_total = sum(
            [i.balance for i in equity]
        ) +  net_profit - drawings

        context.update({
            'date': datetime.date.today(),
            'current_assets': current_assets,
            'inventory': inventory,
            'current_assets_total': current_assets_total,
            'long_term_assets': long_term_assets,
            'long_term_assets_total': long_term_assets_total,
            'working_capital': working_capital,
            'current_liabilities': current_liabilities,
            'net_profit': net_profit,
            'net_assets': net_assets,
            'current_liabilities_total': current_liabilities_total,
            'long_term_liabilities': long_term_liabilities,
            'long_term_liabilities_total': long_term_liabilities_total,
            'equity': equity,
            'equity_total': equity_total,
            'drawings': drawings,
            'total_assets': current_assets_total + long_term_assets_total,
            
        })
        #insert config !!!
        return context
        
    def get_context_data(self, *args, **kwargs):
        context = super(BalanceSheet, self).get_context_data(*args, **kwargs)
        context['pdf_link'] = True
        return BalanceSheet.common_context(context)

class BalanceSheetPDFView(ConfigMixin, PDFTemplateView):
    template_name = BalanceSheet.template_name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return BalanceSheet.common_context(context)

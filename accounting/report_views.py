import os 
import datetime
import decimal

from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView
from django.db.models import Q
from django.urls import reverse_lazy

from common_data.utilities import ExtraContext, extract_period
from common_data.forms import PeriodReportForm

from . import models 
from . import forms 

class BalanceSheet(TemplateView):
    template_name = os.path.join('accounting', 'reports', 'balance_sheet.html')

    def get_context_data(self, *args, **kwargs):
        context = super(BalanceSheet, self).get_context_data(*args, **kwargs)
        
        #CURRENT ASSETS 
        current_assets = models.Account.objects.filter(
            Q(balance_sheet_category='current-assets')).exclude(
                Q(balance=0) | Q(name__startswith="Customer"))

        customer_accounts = models.Account.objects.filter(
            name__startswith="Customer")

        customer_total = reduce(lambda x, y: x + y,
            [i.balance for i in  customer_accounts], 0 
        )

        current_assets_total = reduce(lambda x, y: x + y,
            [i.balance for i in current_assets], customer_total 
        )

        #LONG TERM ASSETS
        long_term_assets = models.Account.objects.filter(
            Q(balance_sheet_category='long-term-assets')).exclude(
                Q(balance=0))

        long_term_assets_total = reduce(lambda x, y: x + y,
            [i.balance for i in long_term_assets], 0 
        )

        #LONG TERM LIABILITIES
        long_term_liabilities = models.Account.objects.filter(
            Q(balance_sheet_category='long-term-liabilities')).exclude(
                Q(balance=0))

        long_term_liabilities_total = reduce(lambda x, y: x + y,
            [i.balance for i in long_term_liabilities], 0 
        )

        #CURRENT LIABILITIES
        current_liabilities = models.Account.objects.filter(
            Q(balance_sheet_category='current-liabilities')).exclude(
                Q(balance=0))

        supplier_accounts = models.Account.objects.filter(
            name__startswith="Supplier")

        accounts_payable = reduce(lambda x, y: x + y,
            [i.balance for i in  supplier_accounts], 0 
        )

        current_liabilities_total = reduce(lambda x, y: x + y,
            [i.balance for i in current_liabilities], accounts_payable 
        )

        #EQUITY
        equity = models.Account.objects.filter(
            Q(balance_sheet_category='equity')).exclude(
                Q(balance=0))

        equity_total = reduce(lambda x, y: x + y,
            [i.balance for i in equity], 0 
        )

        context.update({
            'date': datetime.date.today(),
            'current_assets': current_assets,
            'current_assets_total': current_assets_total,
            'accounts_receivable': customer_total,
            'long_term_assets': long_term_assets,
            'long_term_assets_total': long_term_assets_total,
            'current_liabilities': current_liabilities,
            'accounts_payable': accounts_payable,
            'current_liabilities_total': current_liabilities_total,
            'long_term_liabilities': long_term_liabilities,
            'long_term_liabilities_total': long_term_liabilities_total,
            'equity': equity,
            'equity_total': equity_total,
            'total_assets': current_assets_total + long_term_assets_total,
            'total_l_and_e': equity_total + current_liabilities_total + \
                long_term_liabilities_total
        })
        #insert config !!!
        return context


class IncomeStatementFormView(ExtraContext, FormView):
    form_class = PeriodReportForm
    template_name = os.path.join('common_data', 'reports', 'report_form.html')
    extra_context = {
        'action': reverse_lazy('accounting:income-statement'),
        'title': 'Income Statement Report Form'
    }

class IncomeStatement(TemplateView):
    template_name = os.path.join('accounting', 'reports', 'income_statement.html')

    def get_context_data(self, *args, **kwargs):
        context = super(IncomeStatement, self).get_context_data(*args, **kwargs)
        kwargs =  self.request.GET
        start, end = extract_period(kwargs)

        expenses = models.Expense.objects.filter(
            Q(date__gte=start) & Q(date__lte=end)
        )
        expense_totals = {}
        for e in expenses:
            expense_totals[models.expense_choices[e.category]] = \
                 expense_totals.get(models.expense_choices[e.category], 0) + \
                    e.amount

        # only for received invoices
        #!! insert invoices
        #include non cash sales

        #sales tax
        net_sales = 0 #fix

        # modify accounts to support interest
        
        interest_income = 0
        total_revenue = interest_income + net_sales
        
        total_expenses = reduce(lambda x,y: x + y, 
            expense_totals.values(), decimal.Decimal(0.0))

        #insert config

        context.update({
            'start': start,
            'end': end,
            'expenses': expense_totals.items(),
            'net_income': total_revenue - total_expenses,
            'net_sales': net_sales,
            'interest_income': interest_income,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses
        })
        
        return context
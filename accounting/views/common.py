# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal
import json
import os
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework import viewsets, generics
from django.shortcuts import get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from formtools.wizard.views import SessionWizardView

from common_data.utilities import ContextMixin, apply_style, ConfigWizardBase
from common_data.views import PaginationMixin
from invoicing.models import Customer
from accounting import filters, forms, models, serializers
from accounting.views.reports.balance_sheet import BalanceSheet
from accounting.views.dash_plotters import expense_plot, revenue_vs_expense_plot
from employees.forms import EmployeeForm
from employees.models import Employee

#constants

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class Dashboard( TemplateView):
    template_name = os.path.join('accounting', 'dashboard.html')

    def get(self, *args, **kwargs):
        config = models.AccountingSettings.objects.first()
        if config is None:
            config = models.AccountingSettings.objects.create(is_configured = False)
        if config.is_configured:
            return super().get(*args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy('accounting:config-wizard'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bsheet = BalanceSheet.common_context({})
        context['assets'] = bsheet['total_assets']
        context['liabilities'] = bsheet['current_liabilities_total'] + \
            bsheet['long_term_liabilities_total']
        context['equity'] = bsheet['equity_total']
        expense_chart = expense_plot()
        if expense_chart:
            context['expense_graph'] = expense_chart.render(is_unicode=True)
        else:
            context['expense_graph'] = "No expenses were recorded over the last 30 days"

        context['revenue_graph'] = revenue_vs_expense_plot().render(is_unicode=True)    
        return context


#############################################################
#                 JournalEntry Views                         #
#############################################################

# update and delete removed for security, only adjustments can alter the state 
# of an entry 

class JournalEntryCreateView( ContextMixin, CreateView):
    '''This type of journal entry has only one credit and one debit'''
    template_name = CREATE_TEMPLATE
    model = models.JournalEntry
    form_class = forms.SimpleJournalEntryForm
    
    extra_context = {
        "title": "Create New Journal Entry",
        "description": "Register Financial Transactions with the accounting system."
        }

    def get_success_url(self):
        return '/accounting/entry-detail/{}'.format(self.object.pk) 

class JournalEntryIframeView(ListView):
    template_name = os.path.join('accounting', 'journal', 'entry_list.html')
    paginate_by = 20
    def get_queryset(self):
        return models.JournalEntry.objects.filter(
            journal= models.Journal.objects.get(pk=self.kwargs['pk'])
        ).order_by('date')


class ComplexEntryView( ContextMixin, CreateView):
    '''This type of journal entry can have any number of 
    credits and debits. The front end page uses react to dynamically 
    alter the content of page hence the provided data from react is 
    sent to the server as urlencoded json in a hidden field called items[]
    
    '''
    template_name = os.path.join('accounting', 'compound_transaction.html')
    form_class= forms.ComplexEntryForm

    def post(self, request, *args, **kwargs):
        j = models.JournalEntry.objects.create(
                memo = request.POST['memo'],
                date = request.POST['date'],
                journal = models.Journal.objects.get(
                    pk=request.POST['journal']),
                created_by = request.user
            )
        for item in request.POST.getlist('items[]'):
            item_data = json.loads(urllib.parse.unquote(item))
            amount = decimal.Decimal(item_data['amount'])
                #incase the name includes '-' character
            pk, _ = item_data['account'].split("-")[:2] 
            account = models.Account.objects.get(
                    pk=int(pk))
            #make sure
            if int(item_data['debit']) == 1:
                j.debit(amount, account)
            else:
                j.credit(amount, account)

        return HttpResponseRedirect(reverse_lazy('accounting:dashboard'))

class JournalEntryDetailView( DetailView):
    template_name = os.path.join('accounting', 'transaction_detail.html')
    model = models.JournalEntry

#############################################################
#                 Account  Views                            #
#############################################################
class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer


class AccountTransferPage( ContextMixin, CreateView):
    template_name = os.path.join('common_data','crispy_create_template.html')
    success_url = reverse_lazy('accounting:dashboard')
    form_class = forms.SimpleJournalEntryForm
    extra_context = {
        'title': 'Transfer between Accounts',
        'description': 'Move money directly between accounts using a simplified interface. Journal Entries are created automatically'
    }

class AccountCreateView( ContextMixin, CreateView):
    template_name = os.path.join('common_data','crispy_create_template.html')
    model = models.Account
    form_class = forms.AccountForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {
        "title": "Create New Account",
        'description': "Use accounts to manage income and expenses in an intuitive way. A default chart of expenses is already implemented."}

class AccountUpdateView( ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    model = models.Account
    form_class = forms.AccountUpdateForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {"title": "Update Existing Account"}


class AccountDetailView( DetailView):
    template_name = os.path.join('accounting', 'account','detail.html')
    model = models.Account 
    

class AccountCreditIframeView(ListView):
    template_name = os.path.join('accounting', 'account', 'entry_list.html')
    paginate_by = 20
    def get_queryset(self):
        return models.Credit.objects.filter(
            account= models.Account.objects.get(pk=self.kwargs['pk']),
            entry__draft=False
        ).order_by('pk')


class AccountDebitIframeView(ListView):
    template_name = os.path.join('accounting', 'account', 'entry_list.html')
    paginate_by = 20
    def get_queryset(self):
        return models.Debit.objects.filter(
            account= models.Account.objects.get(pk=self.kwargs['pk']),
            entry__draft=False
        ).order_by('pk')


class AccountListView( PaginationMixin, FilterView,  
        ContextMixin):
    template_name = os.path.join('accounting', 'account','list.html')
    filterset_class = filters.AccountFilter
    paginate_by = 20
    queryset = models.Account.objects.all()
    extra_context = {
        "title": "Chart of Accounts",
        'new_link': reverse_lazy('accounting:create-account')
                }
    #model=models.Account

#############################################################
#                        Misc Views                         #
#############################################################

class TaxViewset(viewsets.ModelViewSet):
    queryset = models.Tax.objects.all()
    serializer_class = serializers.TaxSerializer

class TaxUpdateView( ContextMixin, UpdateView):
    form_class = forms.TaxUpdateForm
    model= models.Tax
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Edit Sales Tax'
    }

class TaxCreateView( ContextMixin, CreateView):
    form_class = forms.TaxForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Add Sales Taxes',
        'description': 'Sales taxes are used in orders and invoices.',
        
    }


class TaxListView( ContextMixin, PaginationMixin, FilterView):
    filterset_class = filters.TaxFilter
    template_name = os.path.join('accounting','tax_list.html')
    paginate_by = 20
    model = models.Tax
    extra_context = {
        'title': 'Sales Tax List',
        'new_link': reverse_lazy('accounting:create-tax')
    }

class TaxDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:util-list')
    model = models.Tax

class DirectPaymentFormView( ContextMixin, FormView):
    '''Uses a simple form view as a wrapper for a transaction in the journals
    for transactions involving two accounts.
    '''
    form_class = forms.DirectPaymentForm
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {'title': 'Create Direct Payment'}

    def get_initial(self):
        if self.kwargs.get('supplier', None):
            return {
                'paid_to': self.kwargs['supplier']
            }
            
        return {}

    def post(self, request):
        resp = super(DirectPaymentFormView, self).post(request)
        form = self.form_class(request.POST)
        if form.is_valid():
            notes_string = """
                This payment was made out to: %s.
                the payment method used: %s \n """ % \
                (form.cleaned_data['paid_to'],
                    form.cleaned_data['method'])
            journal = models.Journal.objects.get(
                pk=4)#purchases journal
            j = models.JournalEntry.objects.create(
                memo=notes_string + form.cleaned_data['notes'],
                date=form.cleaned_data['date'],
                journal = journal,
                created_by=request.user
            )
            j.simple_entry(
                form.cleaned_data['amount'],
                form.cleaned_data['paid_to'].account,
                form.cleaned_data['account_paid_from'],
            )
        return resp

class AccountConfigView( UpdateView):
    '''
    Tabbed Configuration view for accounts 
    '''
    form_class = forms.ConfigForm
    template_name = os.path.join('accounting', 'config.html')
    success_url = reverse_lazy('accounting:dashboard')
    model = models.AccountingSettings

class DirectPaymentList( ContextMixin, TemplateView):
    template_name = os.path.join('accounting', 'direct_payment_list.html')
    extra_context = {
        'entries': lambda : models.JournalEntry.objects.filter(
           journal = models.Journal.objects.get(pk=4)) 
    }

#############################################################
#                    Journal Views                         #
#############################################################

class JournalCreateView( ContextMixin, CreateView):
    template_name = CREATE_TEMPLATE
    model = models.Journal
    form_class = forms.JournalForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {
        "title": "Create New Journal",
        "description": 'A virtual document used to record all financial transactions in a business.'}

class JournalDetailView( DetailView):
    template_name = os.path.join('accounting', 'journal', 'detail.html')
    model = models.Journal

class JournalListView( ContextMixin, PaginationMixin, FilterView):
    template_name = os.path.join('accounting', 'journal', 'list.html')
    filterset_class = filters.JournalFilter
    paginate_by = 20
    extra_context = {
        "title": "Accounting Journals",
        'new_link': reverse_lazy('accounting:create-journal')
                }

    def get_queryset(self):
        return models.Journal.objects.all().order_by('name')

    

#########################################################
#                  Assets and Expenses                  #
#########################################################

class ExpenseAPIView(viewsets.ModelViewSet):
    queryset = models.Expense.objects.all()
    serializer_class = serializers.ExpenseSerializer


class CustomerExpenseAPIView(generics.ListAPIView):
    serializer_class = serializers.ExpenseSerializer
    
    def get_queryset(self):
        customer = Customer.objects.get(pk=self.kwargs['customer'])
        return models.Expense.objects.filter(customer=customer)

class AssetCreateView(ContextMixin,  CreateView):
    form_class = forms.AssetForm
    template_name = os.path.join('common_data','crispy_create_template.html')
    success_url = "/accounting/"
    extra_context = {
        'title': 'Register New Asset',
        'description': 'Used to formally record valuable property belonging to the organization'
    }

    def post(self, *args, **kwargs):
        resp = super().post(*args, **kwargs)
        if self.object:
            self.object.create_entry()

        return resp
        
class AssetUpdateView(ContextMixin,  UpdateView):
    form_class = forms.AssetForm
    template_name = CREATE_TEMPLATE
    success_url = "/accounting/"
    extra_context = {
        'title': 'Update Asset Data'
    }
    model = models.Asset


class AssetListView(ContextMixin,  PaginationMixin, 
        FilterView):
    template_name = os.path.join('accounting', 'asset_list.html')
    model = models.Asset
    filterset_class = filters.AssetFilter
    extra_context = {
        'title': 'List of Assets',
        'new_link': reverse_lazy('accounting:asset-create')
    }


class AssetDetailView( DetailView):
    template_name = os.path.join('accounting', 'asset_detail.html')
    model = models.Asset

class ExpenseCreateView(ContextMixin,  CreateView):
    form_class = forms.ExpenseForm
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = "/accounting/"
    extra_context = {
        'title': 'Record Expense',
        'description': 'Record costs incurred in the process of running a business.'
    }

    def post(self, *args, **kwargs):
        resp =super().post(*args, **kwargs)
        if self.object:
            self.object.create_entry()
        return resp

class ExpenseListView(ContextMixin,  PaginationMixin, 
        FilterView):
    template_name = os.path.join('accounting', 'expense_list.html')
    model = models.Expense
    filterset_class = filters.ExpenseFilter
    extra_context = {
        'title': 'List of Expenses',
        'new_link': reverse_lazy('accounting:expense-create')
    }


class ExpenseDetailView( DetailView):
    template_name = os.path.join('accounting', 'expense_detail.html')
    model = models.Expense

class ExpenseDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.Expense
    success_url = "/accounting/expense-list"

class RecurringExpenseCreateView(ContextMixin,  
        CreateView):
    form_class = forms.RecurringExpenseForm
    template_name = os.path.join('common_data','crispy_create_template.html')
    success_url = "/accounting/"
    extra_context = {
        'title': 'Record Recurring Expense',
        'description': 'Record costs that occur periodically'
    }

class RecurringExpenseUpdateView(ContextMixin,  
        UpdateView):
    form_class = forms.RecurringExpenseForm
    template_name = CREATE_TEMPLATE
    success_url = "/accounting/"
    extra_context = {
        'title': 'Update Recurring Expense'
    }
    model = models.RecurringExpense

class RecurringExpenseListView(ContextMixin,  
        PaginationMixin, FilterView):
    template_name = os.path.join('accounting', 'recurring_expense_list.html')
    model = models.RecurringExpense
    filterset_class = filters.RecurringExpenseFilter
    extra_context = {
        'title': 'List of Recurring Expenses',
        'new_link': reverse_lazy('accounting:recurring-expense-create')
    }


class RecurringExpenseDetailView( DetailView):
    template_name = os.path.join('accounting', 'recurring_expense_detail.html')
    model = models.RecurringExpense

class RecurringExpenseDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.RecurringExpense
    success_url = "/accounting/recurring-expense/list"



####################################################
#                  Bookeeper                       #
####################################################

class BookkeeperCreateView( CreateView):
    form_class = forms.BookkeeperForm
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy('accounting:bookkeeper-list')
    extra_context = {
        'title': 'Create Bookkeeper',
        'description': 'Assign An existing employee the role of Bookkeeper to manage the accounting system.'
    }

class BookkeeperUpdateView( UpdateView):
    form_class = forms.BookkeeperForm
    template_name = CREATE_TEMPLATE
    queryset = models.Bookkeeper.objects.all()
    success_url = reverse_lazy('accounting:bookkeeper-list')
    extra_context = {
        'title': 'Update Bookkeeper features'
    }

class BookkeeperListView( PaginationMixin ,FilterView):
    queryset = models.Bookkeeper.objects.filter(active=True)
    paginate_by = 20
    template_name = os.path.join('accounting', 'bookkeeper_list.html')
    extra_context = {
        'title': 'List of Bookkeepers',
        'new_link': reverse_lazy('accounting:create-bookkeeper')
    }
    filterset_class = filters.BookkeeperFilter


class BookkeeperDetailView( DetailView):
    model = models.Bookkeeper
    template_name = os.path.join('accounting', 'bookkeeper_detail.html')
    
    
class BookkeeperDeleteView(ContextMixin,  DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.Bookkeeper
    extra_context = {
        'title': 'Delete Bookkeeper'
    }


class CurrencyConverterView( TemplateView):
    template_name = os.path.join('accounting', 'currency_converter.html')

class CurrencyCreateView( CreateView):
    template_name = CREATE_TEMPLATE
    model = models.Currency
    fields = "__all__"
    success_url = "accounting/currency-converter"

class CurrencyUpdateView( UpdateView):
    template_name = CREATE_TEMPLATE
    model = models.Currency
    fields = "__all__"
    success_url = "accounting/currency-converter"


class CurrencyConversionLineCreateView( 
        CreateView):
    template_name = CREATE_TEMPLATE
    model = models.CurrencyConversionLine
    fields = "__all__"
    success_url = "accounting/currency-converter"

class CurrencyConversionLineUpdateView( 
        UpdateView):
    template_name = CREATE_TEMPLATE
    model = models.CurrencyConversionLine
    fields = "__all__"
    success_url = "accounting/currency-converter"

class CurrencyAPIView(viewsets.ModelViewSet):
    queryset = models.Currency.objects.all()
    serializer_class = serializers.CurrencySerializer

class CurrencyConversionLineAPIView(viewsets.ModelViewSet):
    queryset = models.CurrencyConversionLine.objects.all()
    serializer_class = serializers.CurrencyConversionLineSerializer

class CurrencyConversionTableAPIView(viewsets.ModelViewSet):
    queryset = models.CurrencyConversionTable.objects.all()
    serializer_class = serializers.CurrencyConversionTableSerializer


class ExchangeTableCreateView(CreateView):
    # no get only post
    form_class = forms.ExchangeTableForm
    success_url = "/accounting/currency-converter/"
    template_name = CREATE_TEMPLATE

def update_reference_currency(request, table=None, currency=None):
    table = models.CurrencyConversionTable.objects.get(pk=table)
    currency = models.Currency.objects.get(pk=currency)
    table.reference_currency = currency
    table.save()

    return JsonResponse({'status': 'ok'})


def exchange_rate(request, line=None):
    line = models.CurrencyConversionLine.objects.get(pk=line)
    line.exchange_rate  = request.POST['rate']
    line.save()
    return JsonResponse({'status': 'ok'})

def create_exchange_table_conversion_line(request):
    table = models.CurrencyConversionTable.objects.get(
        pk=request.POST['table_id']) 
    currency = models.Currency.objects.get(
        pk=request.POST['currency_id']
    )
    models.CurrencyConversionLine.objects.create(
        currency = currency,
        exchange_rate = request.POST['rate'],
        conversion_table = table
    )
    return JsonResponse({'status': 'ok'})

def verify_entry(request, pk=None):
    entry = get_object_or_404(models.JournalEntry, pk=pk)
    entry.verify()
    return HttpResponseRedirect('/accounting/entry-detail/{}'.format(pk))


def employee_condition(self):
    return Employee.objects.all().count() == 0

def bookkeeper_condition(self):
    return models.Bookkeeper.objects.all().count() == 0

class ConfigWizard(ConfigWizardBase):
    template_name = os.path.join('accounting', 'wizard.html')
    form_list = [
        forms.ConfigForm, 
        EmployeeForm,
        forms.BookkeeperForm, 
        forms.TaxForm
    ]

    condition_dict = {
        '1': employee_condition,
        '2': bookkeeper_condition
    }

    config_class = models.AccountingSettings
    success_url = reverse_lazy('accounting:dashboard')
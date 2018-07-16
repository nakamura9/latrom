# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib
import datetime
import decimal

from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView,  FormView
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django_filters.views import FilterView
from django.urls import reverse_lazy
from rest_framework import viewsets

import serializers
import models 
import filters
import forms
from inventory.models import Item
from common_data.utilities import ExtraContext, load_config, apply_style, ModelViewGroup

#constants
CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('accounting', 'dashboard.html')

#############################################################
#                 JournalEntry Views                         #
#############################################################

# update and delete removed for security, only adjustments can alter the state 
# of an entry 

class JournalEntryCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    '''This type of journal entry has only one credit and one debit'''
    template_name = CREATE_TEMPLATE
    model = models.JournalEntry
    form_class = forms.SimpleJournalEntryForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {"title": "Create New Journal Entry"}

class ComplexEntryView(LoginRequiredMixin, ExtraContext, CreateView):
    '''This type of journal entry can have any number of 
    credits and debits. The front end page uses react to dynamically 
    alter the content of page hence the provided data from react is 
    sent to the server as urlencoded json in a hidden field called items[]
    
    '''
    template_name = os.path.join('accounting', 'compound_transaction.html')
    form_class= forms.ComplexEntryForm

    def post(self, request, *args, **kwargs):
        j = models.JournalEntry.objects.create(
                reference = request.POST['reference'],
                memo = request.POST['memo'],
                date = request.POST['date'],
                journal = models.Journal.objects.get(
                    pk=request.POST['journal']),
            )
        for item in request.POST.getlist('items[]'):
            item_data = json.loads(urllib.unquote(item))
            amount = decimal.Decimal(item_data['amount'])
            account = models.Account.objects.get(
                    pk=int(item_data['account']))
            #make sure
            if int(item_data['debit']) == 1:
                j.debit(amount, account)
            else:
                j.credit(amount, account)

        return HttpResponseRedirect(reverse_lazy('accounting:dashboard'))

class JournalEntryDetailView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('accounting', 'transaction_detail.html')
    model = models.JournalEntry

#############################################################
#                 Account  Views                            #
#############################################################
class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer


class AccountTransferPage(LoginRequiredMixin, ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy('accounting:dashboard')
    form_class = forms.SimpleJournalEntryForm
    extra_context = {
        'title': 'Transfer between Accounts'
    }

class AccountCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    model = models.Account
    form_class = forms.AccountForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {"title": "Create New Account"}

class AccountUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    template_name = CREATE_TEMPLATE
    model = models.Account
    form_class = forms.AccountUpdateForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {"title": "Update Existing Account"}


class AccountDetailView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('accounting', 'account_detail.html')
    model = models.Account 
    

class AccountListView(LoginRequiredMixin, ExtraContext, FilterView):
    template_name = os.path.join('accounting', 'account_list.html')
    filterset_class = filters.AccountFilter
    paginate_by = 10
    extra_context = {
        "title": "Chart of Accounts",
        'new_link': reverse_lazy('accounting:create-account')
                }
    def get_queryset(self):
        return models.Account.objects.filter(active=True).order_by('pk')
#############################################################
#                        Misc Views                         #
#############################################################

class TaxViewset(viewsets.ModelViewSet):
    queryset = models.Tax.objects.all()
    serializer_class = serializers.TaxSerializer

class TaxUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    form_class = forms.TaxForm
    model= models.Tax
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Editing Existing Tax'
    }

class TaxCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    form_class = forms.TaxForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Add Taxes For Invoices'
    }

class TaxDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:util-list')
    model = models.Tax

class DirectPaymentFormView(LoginRequiredMixin, ExtraContext, FormView):
    '''Uses a simple form view as a wrapper for a transaction in the journals
    for transactions involving two accounts.
    '''
    form_class = forms.DirectPaymentForm
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {'title': 'Create Direct Payment'}
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
                reference = 'DPMT:' + form.cleaned_data['reference'],
                memo=notes_string + form.cleaned_data['notes'],
                date=form.cleaned_data['date'],
                journal = journal
            )
            j.simple_entry(
                form.cleaned_data['amount'],
                form.cleaned_data['paid_to'].account,
                form.cleaned_data['account_paid_from'],
            )
        return resp

class AccountConfigView(LoginRequiredMixin, FormView):
    '''
    Tabbed Configuration view for accounts 
    '''
    form_class = forms.ConfigForm
    template_name = os.path.join('accounting', 'config.html')
    success_url = reverse_lazy('accounting:dashboard')
    
    def get_initial(self):
        return load_config()

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            config = load_config()
            new_config = dict(config)
            new_config.update(request.POST.dict())
            json.dump(new_config, open('config.json', 'w'))

        return super(AccountConfigView, self).post(request)

class NonInvoicedCashSale(LoginRequiredMixin, FormView):
    '''
    A transaction handled entirely in the accounting part of the application
    No invoice is generated but the relevant accounts are transacted on and 
    the appropriate inventory is updated.
    React is used to provide a table of items that can be added to the cash
    sale. It communicates with the server in the form of json submitted as 
    part of a number of hidden fields called 'items[]'.
    '''
    form_class = forms.NonInvoicedSaleForm
    template_name = os.path.join('accounting', 'non_invoiced_cash_sale.html')
    success_url = reverse_lazy('accounting:dashboard')

    def post(self, request, *args, **kwargs):
        resp = super(NonInvoicedCashSale, self).post(request, *args, **kwargs)
        total = 0
        config = load_config()
        form =self.form_class(request.POST)
        
        #clean data
        if form.is_valid():
            for item in request.POST.getlist('items[]'):
                data = json.loads(urllib.unquote(item))
                quantity = float(data['quantity'])
                item = Item.objects.get(pk=data['code'])
                #update inventory
                warehouse =form.cleaned_data['sold_from']
                if warehouse.has_item(item):
                    warehouse.decrement_item(item, quantity)
                
                amount_sold = item.unit_sales_price * decimal.Decimal(quantity) 
                discount = amount_sold * decimal.Decimal(float(data['discount']) / 100.0)
                total += amount_sold - discount
                # record discounts in accounts
                #fix
                date = form.cleaned_data['date'].strftime('%Y-%m-%d')
            
            #add taxes here from the config


            j = models.JournalEntry.objects.create(
                    date=date,
                    memo = request.POST['comments'],
                    reference = "Journal Entry derived from non invoiced cash sale",
                    journal = models.Journal.objects.get(pk=3)#sales journal
                    
                )
            j.simple_entry(
                total,
                models.Account.objects.get(pk=1004),#inventory
                models.Account.objects.get(pk=1000),#sales
            )
        return resp

class DirectPaymentList(LoginRequiredMixin, ExtraContext, TemplateView):
    template_name = os.path.join('accounting', 'direct_payment_list.html')
    extra_context = {
        'entries': lambda : models.JournalEntry.objects.filter(
           journal = models.Journal.objects.get(pk=4)) 
    }

#############################################################
#                    Journal Views                         #
#############################################################

class JournalCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    model = models.Journal
    form_class = forms.JournalForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {"title": "Create New Journal"}

class JournalDetailView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('accounting', 'journal_detail.html')
    model = models.Journal

class JournalListView(LoginRequiredMixin, ExtraContext, FilterView):
    template_name = os.path.join('accounting', 'journal_list.html')
    filterset_class = filters.JournalFilter
    paginate_by = 10
    extra_context = {
        "title": "Accounting Journals",
        'new_link': reverse_lazy('accounting:create-journal')
                }

    def get_queryset(self):
        return models.Journal.objects.all().order_by('name')

#########################################################
#                  Assets and Expenses                  #
#########################################################

class AssetViewGroup(ModelViewGroup):
    model = models.Asset
    create_form = forms.AssetForm
    create_template = os.path.join('accounting', 'asset_create.html')
    list_template = os.path.join('accounting', 'asset_list.html')
    delete_template = os.path.join('common_data', 'delete_template.html')
    success_url = "/accounting/"

class ExpenseViewGroup(ModelViewGroup):
    model = models.Expense
    create_form = forms.ExpenseForm
    create_template = os.path.join('accounting','expense_create.html')
    list_template = os.path.join('accounting', 'expense_list.html')
    delete_template = os.path.join('common_data', 'delete_template.html')
    success_url = "/accounting/"

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json
import urllib
import datetime

from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView,  FormView
from django.http import HttpResponseRedirect
from django_filters.views import FilterView
from django.db.models import Q
from django.urls import reverse_lazy
from rest_framework import viewsets

import serializers
import models 
import filters
import forms
from inventory.models import Item
from common_data.utilities import ExtraContext, load_config, apply_style

#constants
CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class Dashboard(TemplateView):
    template_name = os.path.join('accounting', 'dashboard.html')

#############################################################
#                 Transaction Views                         #
#############################################################


# update and delete removed for security, only adjustments can alter the state 
# of a transaction 

class TransactionCreateView(ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    model = models.Transaction
    form_class = forms.TransactionForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {"title": "Create New Transaction"}

class CompoundTransactionView(ExtraContext, CreateView):
    template_name = os.path.join('accounting', 'compound_transaction.html')
    form_class= forms.CompoundTransactionForm


    def post(self, request, *args, **kwargs):
        
        for item in request.POST.getlist('items[]'):
            item_data = json.loads(urllib.unquote(item))
            
            trans = models.Transaction(
                reference = request.POST['reference'],
                memo = request.POST['memo'],
                date = request.POST['date'],
                Journal = models.Journal.objects.get(
                    pk=request.POST['Journal']),
                amount = item_data['amount'],
            )

            if item_data['debit'] == '1':
                trans.debit = models.Account.objects.get(
                    pk=int(item_data['account']))
            else:
                trans.credit = models.Account.objects.get(
                    pk=int(item_data['account']))
            trans.save()
        return HttpResponseRedirect(reverse_lazy('accounting:dashboard'))

class TransactionDetailView(DeleteView):
    template_name = os.path.join('accounting', 'transaction_detail.html')
    model = models.Transaction

#############################################################
#                 Employee  Views                            #
#############################################################

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer

class EmployeeCreateView(ExtraContext, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('accounting:dashboard')
    form_class = forms.EmployeeForm
    extra_context = {
        'title': 'Add Employee to payroll system'
    }

class EmployeeUpdateView(ExtraContext, UpdateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('accounting:dashboard')
    form_class = forms.EmployeeForm
    model = models.Employee
    extra_context = {
        'title': 'Edit Employee data on payroll system'
    }

class EmployeeListView(ExtraContext, FilterView):
    template_name = os.path.join('accounting', 'employee_list.html')
    filterset_class = filters.EmployeeFilter
    extra_context = {
        'title': 'List of Employees',
        'new_link': reverse_lazy('accounting:create-employee')
    }

class EmployeeDetailView(DetailView):
    template_name = os.path.join('accounting', 'employee_detail.html')
    model = models.Employee

class EmployeeDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('accounting:list-employees')
    model = models.Employee



#############################################################
#                 Account  Views                            #
#############################################################
class AccountViewSet(viewsets.ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer


class AccountTransferPage(ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy('accounting:dashboard')
    form_class = forms.TransferForm
    extra_context = {
        'title': 'Transfer between Accounts'
    }

class AccountCreateView(ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    model = models.Account
    form_class = forms.AccountForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {"title": "Create New Account"}

class AccountUpdateView(ExtraContext, UpdateView):
    template_name = CREATE_TEMPLATE
    model = models.Account
    form_class = forms.AccountForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {"title": "Update Existing Account"}


class AccountDetailView(DetailView):
    template_name = os.path.join('accounting', 'account_detail.html')
    model = models.Account 
    #implemnt filter functionality
    def get_context_data(self, *args, **kwargs):
        #implemented because related manager not getting all transactions 
        context = super(AccountDetailView, self).get_context_data(*args, **kwargs)
        context['transactions'] = models.Transaction.objects.filter(
            Q(credit=self.object) | Q(debit=self.object))
        return context

class AccountListView(ExtraContext, FilterView):
    template_name = os.path.join('accounting', 'account_list.html')
    filterset_class = filters.AccountFilter
    paginate_by = 10
    extra_context = {
        "title": "Chart of Accounts",
        'new_link': reverse_lazy('accounting:create-account')
                }

#############################################################
#                        Misc Views                         #
#############################################################

class TaxViewset(viewsets.ModelViewSet):
    queryset = models.Tax.objects.all()
    serializer_class = serializers.TaxSerializer

class TaxUpdateView(ExtraContext, UpdateView):
    form_class = forms.TaxForm
    model= models.Tax
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {
        'title': 'Editing Existing Tax'
    }

class TaxCreateView(ExtraContext, CreateView):
    form_class = forms.TaxForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('accounting:util-list')
    extra_context = {
        'title': 'Add Taxes For Invoices'
    }

class TaxDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('accounting:util-list')
    model = models.Tax

class DeductionCreateView(ExtraContext, CreateView):
    form_class = forms.DeductionForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {
        'title': 'Add Deductions For Payroll'
    }

class DeductionUpdateView(ExtraContext, UpdateView):
    form_class = forms.DeductionForm
    model = models.Deduction
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('accounting:util-list')
    extra_context = {
        'title': 'Update existing deduction'
    }

class DeductionDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('accounting:util-list')
    model = models.Deduction

class UtilsListView(TemplateView):
    template_name = os.path.join('accounting', 'utils_list.html')

    def get_context_data(self, *args, **kwargs):
        context = super(UtilsListView, self).get_context_data(*args, **kwargs)
        context['allowances'] = models.Allowance.objects.all()
        context['deductions'] = models.Deduction.objects.all()
        context['commissions'] = models.CommissionRule.objects.all()
        context['taxes'] = models.Tax.objects.all()
        return context


class AllowanceCreateView(ExtraContext, CreateView):
    form_class = forms.AllowanceForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {
        'title': 'Create New Allowance '
    }

class AllowanceUpdateView(ExtraContext, UpdateView):
    form_class = forms.AllowanceForm
    model = models.Allowance
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('accounting:util-list')
    extra_context = {
        'title': 'Edit Existing Allowance '
    }

class AllowanceDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('accounting:util-list')
    model = models.Allowance

class CommissionCreateView(ExtraContext, CreateView):
    form_class = forms.CommissionForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {
        'title': 'Add Commission Rule for pay grades'
    }

class CommissionUpdateView(ExtraContext, UpdateView):
    form_class = forms.CommissionForm
    model = models.CommissionRule
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('accounting:util-list')
    extra_context = {
        'title': 'Edit Existing Commission Rule'
    }

class CommissionDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('accounting:util-list')
    model = models.CommissionRule

###################################################
#                 Pay Grade Views                 #
###################################################

class PayGradeCreateView(ExtraContext, CreateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {
        'title': 'Add pay grades for payroll'
    }

class PayGradeUpdateView(ExtraContext, UpdateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {
        'title': 'Edit existing Pay Grade'
    }

class PayGradeListView(ListView):
    template_name = os.path.join('accounting', 'pay_grade_list.html')
    paginate_by = 10
    extra_context = {
        'title': 'List of Payslips'
    }

class PayGradeDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template')
    success_url = reverse_lazy('accounting:list-pay-grades')
    model = models.PayGrade

class NonInvoicedCashSale(FormView):
    form_class = forms.NonInvoicedSaleForm
    template_name = os.path.join('accounting', 'non_invoiced_cash_sale.html')
    success_url = reverse_lazy('accounting:dashboard')

    def get(self, request):
        resp = super(NonInvoicedCashSale, self).get(request)
        print self.get_context_data()
        return resp

    def post(self, request, *args, **kwargs):
        resp = super(NonInvoicedCashSale, self).post(request, *args, **kwargs)
        total = 0
        for item in request.POST.getlist('items[]'):
            data = json.loads(urllib.unquote(item))
            print data
            quantity = float(data['quantity'])
            item = Item.objects.get(pk=data['code'])
            item.quantity -= quantity
            total += (item.unit_sales_price * quantity) * (float(data['discount']) / 100)
            item.save()
            #fix
            date = datetime.datetime.strptime(
                request.POST['date'], '%m/%d/%Y').strftime('%Y-%m-%d')

        models.Transaction(
                date=date,
                amount = total,
                memo = request.POST['comments'],
                reference = "transaction derived from non invoiced cash sale",
                credit=models.Account.objects.get(name='Current Account'),
                debit=models.Account.objects.get(name='General Sales'),
            ).save()
        return resp


#############################################################
#                     Payslip Views                         #
#############################################################

class PayslipView( DetailView):
    
    
    template_name = os.path.join('accounting', 'payslip.html')
    model= models.Payslip

    def get_context_data(self, *args, **kwargs):
        context = super(PayslipView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Pay Slip'
        context.update(load_config())
        return context


class PayslipListView(ExtraContext, FilterView):
    filterset_class = filters.PayslipFilter
    template_name = os.path.join('accounting', 'payslip_list.html')
    paginate_by = 10
    extra_context = {
        'title': 'List of Payslips'
    }

class PayslipViewset(viewsets.ModelViewSet):
    queryset = models.Payslip.objects.all()
    serializer_class = serializers.PayslipSerializer

#############################################################
#                    Journal Views                         #
#############################################################

class JournalCreateView(ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    model = models.Journal
    form_class = forms.JournalForm
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {"title": "Create New Journal"}

class JournalDetailView(DetailView):
    template_name = os.path.join('accounting', 'journal_detail.html')
    model = models.Journal

class JournalListView(ExtraContext, FilterView):
    template_name = os.path.join('accounting', 'journal_list.html')
    filterset_class = filters.JournalFilter
    paginate_by = 10
    extra_context = {
        "title": "Accounting Journals",
        'new_link': reverse_lazy('accounting:create-journal')
                }


#############################################################
#                    PayGrade Views                         #
#############################################################

class PayGradeUpdateView(ExtraContext, UpdateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    model = models.PayGrade
    success_url = reverse_lazy('accounting:dashboard')
    extra_context = {
        'title': 'Update existing pay grade'
    }


class PayGradeListView(ExtraContext, FilterView):
    template_name = os.path.join('accounting', 'pay_grade_list.html')
    extra_context = {
        'title': 'List of Pay Grades'
    }
    model = models.PayGrade

class PayrollConfigView(ExtraContext, TemplateView):
    template_name = os.path.join('accounting', 'payroll_config.html')
    extra_context = {
        'employees': models.Employee.objects.all()
    }





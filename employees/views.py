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
from accounting.models import Tax
from common_data.utilities import ExtraContext, apply_style, ModelViewGroup

#constants
CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class DashBoard(LoginRequiredMixin, ExtraContext, TemplateView):
    template_name = os.path.join('employees', 'dashboard.html')
    extra_context = {
        'employees': models.Employee.objects.all()
    }

class PayrollConfig(ExtraContext, UpdateView):
    model = models.EmployeesSettings
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy("employees:dashboard")
    form_class = forms.EmployeesSettingsForm
    extra_context = {
        'title': 'Configure automated Payroll'
    }

class ManualPayrollConfig(TemplateView):
    template_name = os.path.join('employees', 'manual_config.html')
    

#############################################################
#                 Employee  Views                            #
#############################################################

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer

class EmployeeCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    form_class = forms.EmployeeForm
    extra_context = {
        'title': 'Add Employee to payroll system'
    }
    

class EmployeeUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    form_class = forms.EmployeeForm
    model = models.Employee
    extra_context = {
        'title': 'Edit Employee data on payroll system'
    }

class EmployeeListView(LoginRequiredMixin, ExtraContext, FilterView):
    template_name = os.path.join('employees', 'employee_list.html')
    filterset_class = filters.EmployeeFilter
    extra_context = {
        'title': 'List of Employees',
        'new_link': reverse_lazy('employees:create-employee')
    }
    def get_queryset(self):
        return models.Employee.objects.filter(active=True).order_by('first_name')

class EmployeeDetailView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('employees', 'employee_detail.html')
    model = models.Employee

class EmployeeDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:list-employees')
    model = models.Employee


class DeductionCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    form_class = forms.DeductionForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add Deductions For Payroll'
    }

class DeductionUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    form_class = forms.DeductionForm
    model = models.Deduction
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Update existing deduction'
    }

class DeductionDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:util-list')
    model = models.Deduction

class UtilsListView(LoginRequiredMixin, TemplateView):
    template_name = os.path.join('employees', 'utils_list.html')

    def get_context_data(self, *args, **kwargs):
        context = super(UtilsListView, self).get_context_data(*args, **kwargs)
        context['allowances'] = models.Allowance.objects.filter(active=True).order_by('name')
        context['deductions'] = models.Deduction.objects.filter(active=True).order_by('name')
        context['commissions'] = models.CommissionRule.objects.filter(active=True).order_by('name')
        context['taxes'] = models.PayrollTax.objects.all().order_by('name')
        return context


class AllowanceCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    form_class = forms.AllowanceForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Create New Allowance '
    }

class AllowanceUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    form_class = forms.AllowanceForm
    model = models.Allowance
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Edit Existing Allowance '
    }

class AllowanceDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:util-list')
    model = models.Allowance

class CommissionCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    form_class = forms.CommissionForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add Commission Rule for pay grades'
    }

class CommissionUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    form_class = forms.CommissionForm
    model = models.CommissionRule
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Edit Existing Commission Rule'
    }

class CommissionDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:util-list')
    model = models.CommissionRule



###################################################
#                 Pay Grade Views                 #
###################################################

class PayGradeCreateView(LoginRequiredMixin, ExtraContext, CreateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add pay grades for payroll'
    }

class PayGradeUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Edit existing Pay Grade'
    }

class PayGradeListView(LoginRequiredMixin, ListView):
    template_name = os.path.join('employees', 'pay_grade_list.html')
    paginate_by = 10
    extra_context = {
        'title': 'List of Payslips'
    }

class PayGradeDeleteView(LoginRequiredMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template')
    success_url = reverse_lazy('employees:list-pay-grades')
    model = models.PayGrade



#############################################################
#                     Payslip Views                         #
#############################################################

class PayslipView(LoginRequiredMixin, DetailView):
    template_name = os.path.join('employees', 'payslip.html')
    model= models.Payslip

    def get_context_data(self, *args, **kwargs):
        context = super(PayslipView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Pay Slip'
        return context

class PayslipListView(LoginRequiredMixin, ExtraContext, FilterView):
    filterset_class = filters.PayslipFilter
    template_name = os.path.join('employees', 'payslip_list.html')
    paginate_by = 10
    extra_context = {
        'title': 'List of Payslips'
    }

    def get_queryset(self):
        return models.Payslip.objects.all().order_by('start_period')
        

class PayslipViewset(viewsets.ModelViewSet):
    queryset = models.Payslip.objects.all()
    serializer_class = serializers.PayslipSerializer



#############################################################
#                    PayGrade Views                         #
#############################################################

class PayGradeUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    model = models.PayGrade
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Update existing pay grade'
    }


class PayGradeListView(LoginRequiredMixin, ExtraContext, FilterView):
    template_name = os.path.join('employees', 'pay_grade_list.html')
    extra_context = {
        'title': 'List of Pay Grades'
    }
    model = models.PayGrade


#####################################################
#                   Payroll Tax Forms               #
#####################################################

class PayrollTaxCreateView(LoginRequiredMixin, CreateView):
    template_name = os.path.join('employees','payroll_tax.html')
    form_class = forms.PayrollTaxForm
    success_url = reverse_lazy('employees:dashboard')
    

    def post(self, request):
        resp = super(PayrollTaxCreateView, self).post(request)
        brackets = json.loads(urllib.unquote(request.POST['brackets']))
        payroll_tax = models.PayrollTax.objects.latest('pk')

        for b in brackets:
            payroll_tax.add_bracket(b['lower_limit'], b['upper_limit'],
                b['rate'], b['deduction'])

        return resp

class PayrollTaxUpdateView(LoginRequiredMixin, ExtraContext, UpdateView):
    template_name = os.path.join('common_data','create_template.html')
    form_class = forms.PayrollTaxForm
    success_url = reverse_lazy('employees:dashboard')
    model = models.PayrollTax
    extra_context = {
        'title': 'Update Payroll Tax Object'
    }

class PayrollTaxDetailView(DetailView):
    template_name = os.path.join('employees', 'payroll_tax_detail.html')
    model = models.PayrollTax


class PayrollTaxDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.PayrollTax
    success_url = reverse_lazy('employees:dashboard')
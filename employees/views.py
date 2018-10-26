# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import decimal
import json
import os
import urllib

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework import viewsets

from accounting.models import Tax
from common_data.utilities import ExtraContext, ModelViewGroup, apply_style
from common_data.views import PaginationMixin

from . import filters, forms, models, serializers


class AdministratorCheckMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_superuser:
            return True
        return False


#constants
CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class DashBoard(AdministratorCheckMixin, ExtraContext, TemplateView):
    template_name = os.path.join('employees', 'dashboard.html')
    extra_context = {
        'employees': models.Employee.objects.all()
    }

class PayrollConfig(AdministratorCheckMixin, ExtraContext, UpdateView):
    model = models.EmployeesSettings
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy("employees:dashboard")
    form_class = forms.EmployeesSettingsForm
    extra_context = {
        'title': 'Configure automated Payroll'
    }

class ManualPayrollConfig(AdministratorCheckMixin, TemplateView):
    template_name = os.path.join('employees', 'manual_config.html')
    

#############################################################
#                 Employee  Views                            #
#############################################################

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer

class EmployeeCreateView(AdministratorCheckMixin, ExtraContext, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    form_class = forms.EmployeeForm
    extra_context = {
        'title': 'Add Employee to payroll system'
    }
    

class EmployeeUpdateView(AdministratorCheckMixin, ExtraContext, UpdateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    form_class = forms.EmployeeForm
    model = models.Employee
    extra_context = {
        'title': 'Edit Employee data on payroll system'
    }

class EmployeeListView(AdministratorCheckMixin, ExtraContext, PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'employee_list.html')
    filterset_class = filters.EmployeeFilter
    paginate_by = 10
    extra_context = {
        'title': 'List of Employees',
        'new_link': reverse_lazy('employees:create-employee')
    }
    queryset = models.Employee.objects.filter(active=True).order_by('first_name')

class EmployeeDetailView(AdministratorCheckMixin, DetailView):
    template_name = os.path.join('employees', 'employee_detail.html')
    model = models.Employee

class EmployeeDeleteView(AdministratorCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:list-employees')
    model = models.Employee


class DeductionCreateView(AdministratorCheckMixin, ExtraContext, CreateView):
    form_class = forms.DeductionForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add Deductions For Payroll'
    }

class DeductionUpdateView(AdministratorCheckMixin, ExtraContext, UpdateView):
    form_class = forms.DeductionForm
    model = models.Deduction
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Update existing deduction'
    }

class DeductionDeleteView(AdministratorCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:util-list')
    model = models.Deduction

class UtilsListView(AdministratorCheckMixin, TemplateView):
    template_name = os.path.join('employees', 'utils_list.html')

    def get_context_data(self, *args, **kwargs):
        context = super(UtilsListView, self).get_context_data(*args, **kwargs)
        context['allowances'] = models.Allowance.objects.filter(active=True).order_by('name')
        context['deductions'] = models.Deduction.objects.filter(active=True).order_by('name')
        context['commissions'] = models.CommissionRule.objects.filter(active=True).order_by('name')
        context['taxes'] = models.PayrollTax.objects.all().order_by('name')
        return context


class AllowanceCreateView(AdministratorCheckMixin, ExtraContext, CreateView):
    form_class = forms.AllowanceForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Create New Allowance '
    }

class AllowanceUpdateView(AdministratorCheckMixin, ExtraContext, UpdateView):
    form_class = forms.AllowanceForm
    model = models.Allowance
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Edit Existing Allowance '
    }

class AllowanceDeleteView(AdministratorCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:util-list')
    model = models.Allowance

class CommissionCreateView(AdministratorCheckMixin, ExtraContext, CreateView):
    form_class = forms.CommissionForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add Commission Rule for pay grades'
    }

class CommissionUpdateView(AdministratorCheckMixin, ExtraContext, UpdateView):
    form_class = forms.CommissionForm
    model = models.CommissionRule
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:util-list')
    extra_context = {
        'title': 'Edit Existing Commission Rule'
    }

class CommissionDeleteView(AdministratorCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:util-list')
    model = models.CommissionRule



###################################################
#                 Pay Grade Views                 #
###################################################

class PayGradeCreateView(AdministratorCheckMixin, ExtraContext, CreateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add pay grades for payroll'
    }

class PayGradeUpdateView(AdministratorCheckMixin, ExtraContext, UpdateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    success_url = reverse_lazy('employees:list-pay-grades')
    extra_context = {
        'title': 'Edit existing Pay Grade'
    }
    queryset = models.PayGrade.objects.all()

class PayGradeListView(AdministratorCheckMixin, ListView):
    template_name = os.path.join('employees', 'pay_grade_list.html')
    paginate_by = 10
    queryset =  models.PayGrade.objects.all()
    extra_context = {
        'title': 'List of Pay grades'
    }

class PayGradeDeleteView(AdministratorCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template')
    success_url = reverse_lazy('employees:list-pay-grades')
    model = models.PayGrade



#############################################################
#                     Payslip Views                         #
#############################################################

class PayslipView(AdministratorCheckMixin, DetailView):
    template_name = os.path.join('employees', 'payslip.html')
    model= models.Payslip

    def get_context_data(self, *args, **kwargs):
        context = super(PayslipView, self).get_context_data(*args, **kwargs)
        context['title'] = 'Pay Slip'
        return context

class PayslipListView(AdministratorCheckMixin, ExtraContext, PaginationMixin, FilterView):
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





#####################################################
#                   Payroll Tax Forms               #
#####################################################

class PayrollTaxCreateView(AdministratorCheckMixin, CreateView):
    template_name = os.path.join('employees','payroll_tax.html')
    form_class = forms.PayrollTaxForm
    success_url = reverse_lazy('employees:dashboard')
    

    def post(self, request):
        resp = super(PayrollTaxCreateView, self).post(request)
        brackets = json.loads(urllib.parse.unquote(request.POST['brackets']))
        if not self.object:
            return resp
        
        payroll_tax = self.object

        for b in brackets:
            payroll_tax.add_bracket(b['lower_limit'], b['upper_limit'],
                b['rate'], b['deduction'])

        return resp

class PayrollTaxUpdateView(AdministratorCheckMixin, ExtraContext, UpdateView):
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


class TimeSheetMixin(object):
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        update_flag = isinstance(self, UpdateView)
        
        def get_time(time_string):
            try:
                return datetime.datetime.strptime(time_string, '%H:%M').time()
            except:
                return datetime.datetime.strptime(time_string, '%H:%M:%S').time()
                
        def get_duration(time_string):
            try:
                hr, min = time_string.split(":")
            except:
                hr, min, sec = time_string.split(":")
            return datetime.timedelta(hours=int(hr), minutes=int(min))

        if not self.object:
            return resp

        if update_flag:
            for i in self.object.attendanceline_set.all():
                i.delete()

        raw_data = request.POST['lines']
        line_data = json.loads(urllib.parse.unquote(raw_data))
        for line in line_data:
            try:
                date =datetime.date(
                        self.object.year, 
                        self.object.month,
                        int(line['date']))
            except:
                date = datetime.date(
                        self.object.year, 
                        self.object.month,
                        28)
            models.AttendanceLine.objects.create(
                timesheet=self.object,
                date=date,
                time_in=get_time(line['timeIn']),
                time_out= get_time(line['timeOut']),
                lunch_duration=get_duration(line['breaksTaken']))
        
        return resp

class CreateTimeSheetView(TimeSheetMixin, CreateView):
    template_name = os.path.join('employees', 'timesheet_create_update.html')
    form_class = forms.TimesheetForm
    success_url = reverse_lazy('employees:dashboard')

class ListTimeSheetView(ExtraContext, PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'time_sheet_list.html')
    filterset_class = filters.TimeSheetFilter
    paginate_by = 10
    extra_context ={
        'title': 'Time Sheets',
        'new_link': reverse_lazy('employees:timesheet-create')
    }
    def get_queryset(self):
        
        return models.EmployeeTimeSheet.objects.all()
    

class TimeSheetDetailView(DetailView):
    model = models.EmployeeTimeSheet
    template_name = os.path.join('employees', 'timesheet_detail.html')

class TimeSheetUpdateView(TimeSheetMixin, UpdateView):
    template_name = os.path.join('employees', 'timesheet_create_update.html')
    form_class = forms.TimesheetForm
    queryset = models.EmployeeTimeSheet.objects.all()
    success_url = reverse_lazy('employees:dashboard')

class TimeSheetViewset(viewsets.ModelViewSet):
    queryset = models.EmployeeTimeSheet.objects.all()
    serializer_class = serializers.TimeSheetSerializer

class PayrollOfficerCreateView(ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.PayrollOfficerForm
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add New Payroll Officer'
    }

class PayrollOfficerUpdateView(ExtraContext, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.PayrollOfficerForm
    queryset = models.PayrollOfficer.objects.all()
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Update Payroll Officer'
    }

class PayrollOfficerListView(ExtraContext, FilterView, PaginationMixin):
    template_name = os.path.join('employees', 'payroll_officer_list.html')
    queryset = models.PayrollOfficer.objects.all()
    filterset_class = filters.PayrollOfficerFilter
    extra_context = {
        'title': 'List of Payroll Officers',
        'new_link': reverse_lazy('employees:payroll-officer-create')
    }


class PayrollOfficerDetailView(DetailView):
    model = models.PayrollOfficer
    template_name = os.path.join('employees', 'payroll_officer_detail.html')
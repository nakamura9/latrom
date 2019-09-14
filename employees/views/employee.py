import datetime
import decimal
import json
import os
import urllib

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework import viewsets

from accounting.models import Tax
from common_data.utilities import ContextMixin, apply_style, ConfigWizardBase
from common_data.views import PaginationMixin
from common_data.models import SingletonModel
from collections import OrderedDict

import openpyxl
import csv


from employees import filters, forms, models, serializers

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer

class EmployeeCreateView( ContextMixin, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.EmployeeForm
    extra_context = {
        'title': 'Create Employee',
        'description': 'Use this form to record employee data. Employee objects can be added to payroll, and have their vacation time managed. They can also be linked to users.',
        'related_links': [
            {
                'name': 'Create Contract',
                'url': '/employees/create-contract/'
            }
        ]
    }

    def get(self, request, *args, **kwargs):
        num_employees = models.Employee.objects.filter(active=True).count()

        with open('../license.json') as f:
            license = json.load(f)
            if num_employees >= license['license']['number_employees'] :
                return HttpResponseRedirect('/base/license-error/features')

            
        return super().get(request, *args, **kwargs)
    

class EmployeeUpdateView( ContextMixin, UpdateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.EmployeeForm
    model = models.Employee
    extra_context = {
        'title': 'Edit Employee data on payroll system'
    }


class EmployeePortalUpdateView( ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.EmployeePortalForm
    model = models.Employee
    extra_context = {
        'title': 'Edit Your Personal Information on record'
    }

    def get_success_url(self):
        return f'/employees/portal/dashboard/{self.object.pk}'

class EmployeeListView( ContextMixin, PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'employee', 'list.html')
    filterset_class = filters.EmployeeFilter
    paginate_by = 20
    extra_context = {
        'title': 'List of Employees',
        'new_link': reverse_lazy('employees:create-employee'),
        "action_list": [
            {
                'label': 'Import Employees from Excel',
                'icon': 'file-excel',
                'link': reverse_lazy('employees:import-employees-from-excel')
            },
            {
                'label': 'Create Multiple Employees',
                'icon': 'file-alt',
                'link': reverse_lazy('employees:create-multiple-employees')
            },
        ]
    }
    queryset = models.Employee.objects.filter(active=True).order_by('first_name')

class EmployeeDetailView( DetailView):
    template_name = os.path.join('employees', 'employee', 'detail.html')
    model = models.Employee

class EmployeeDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:list-employees')
    model = models.Employee


class PayrollOfficerCreateView( ContextMixin, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.PayrollOfficerForm
    extra_context = {
        'title': 'Add Payroll Officer',
        'description': 'Payroll officers are employees assigned to manage employee data such as income and vacation time as well as the roles of users within the system.'
    }

class PayrollOfficerUpdateView( ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.PayrollOfficerUpdateForm
    queryset = models.PayrollOfficer.objects.all()
    extra_context = {
        'title': 'Update Payroll Officer'
    }

class PayrollOfficerListView( ContextMixin, PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'payroll_officer_list.html')
    paginate_by = 20
    queryset = models.PayrollOfficer.objects.all()
    filterset_class = filters.PayrollOfficerFilter
    extra_context = {
        'title': 'List of Payroll Officers',
        'new_link': reverse_lazy('employees:payroll-officer-create')
    }


class PayrollOfficerDetailView( DetailView):
    model = models.PayrollOfficer
    template_name = os.path.join('employees', 'payroll_officer_detail.html')

class EmployeeUserCreateView( FormView):
    success_url = reverse_lazy('employees:dashboard')
    template_name = CREATE_TEMPLATE
    extra_context = {
        'title': 'Create New User for Employee'
    }
    form_class = forms.CreateEmployeeUserForm

    def get_initial(self):
        return {
            'employee': self.kwargs['pk']
        }

    def get(self, request, *args, **kwargs):
        num_users = User.objects.filter(is_superuser=False).count()
        with open('../license.json') as f:
            license = json.load(f)
            if num_users >= license['license']['number_users']:
                return HttpResponseRedirect('/base/license-error/features')
        
        return super().get(request, *args, **kwargs)

class EmployeeUserPasswordChangeView( FormView):
    success_url = reverse_lazy('employees:dashboard')
    template_name = CREATE_TEMPLATE
    extra_context = {
        'title': 'Change Employee User Password'
    }
    form_class = forms.EmployeePasswordChangeForm

    def get_initial(self):
        return {
            'employee': self.kwargs['pk']
        }

class EmployeeUserPasswordResetView(FormView):
    success_url = reverse_lazy('employees:dashboard')
    template_name = CREATE_TEMPLATE
    extra_context = {
        'title': 'Reset Employee User Password'
    }
    form_class = forms.EmployeePasswordResetForm

    def get_initial(self):
        return {
            'employee': self.kwargs['pk']
        }
    
    def form_valid(self, form):
        resp = super().form_valid(form)
        messages.info(self.request, f'The password for {form.cleaned_data["employee"]} has been reset')
        return resp


def remove_employee_user(request, pk=None):
    obj = models.Employee.objects.get(pk=pk)

    if obj.user:
        obj.user = None
        obj.save()
    return HttpResponseRedirect(reverse_lazy('employees:dashboard'))

class DepartmentCreateView(ContextMixin, CreateView):
    template_name = os.path.join('common_data','crispy_create_template.html')
    form_class = forms.DepartmentForm
    extra_context = {
        'title': 'Create New Department'
    }

class DepartmentUpdateView(ContextMixin, UpdateView):
    template_name = os.path.join('common_data','crispy_create_template.html')
    form_class = forms.DepartmentForm
    model = models.Department
    extra_context = {
        'title': 'Update Department Details'
    }

class DepartmentDetailView(ContextMixin, DetailView):
    model = models.Department
    template_name = os.path.join('employees', 'department', 'detail.html')

class DepartmentListView(TemplateView):
    template_name = os.path.join('employees', 'department', 'list.html')

class DepartmentAPIView(viewsets.ModelViewSet):
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer


class ConfigWizard(ConfigWizardBase):
    template_name = os.path.join('employees', 'wizard.html')
    form_list = [
        forms.PayrollDateForm, 
        forms.PayGradeForm, 
        forms.EmployeeForm, 
        forms.PayrollOfficerForm, 
        forms.EmployeesSettingsForm
    ]
    success_url = reverse_lazy('employees:dashboard')
    config_class = models.EmployeesSettings


    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if step == '0':
            initial.update({'schedule': 1})

        return initial


class ContractCreateView(ContextMixin,CreateView):
    form_class = forms.ContractForm
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    model = models.Contract
    extra_context = {
        'title': 'Create Employee Contract'
    }

class ContractUpdateView(ContextMixin, UpdateView):
    form_class = forms.ContractForm
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    model = models.Contract
    extra_context = {
        'title': 'Update Contract Details'
    }

class ContractListView(ContextMixin, PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'employee', 'contract', 
        'list.html')
    paginate_by=20
    queryset = models.Contract.objects.all()
    filterset_class = filters.ContractFilter
    extra_context = {
        'title': 'List of Employee Contracts',
        'new_link': reverse_lazy('employees:create-contract')
    }

class ContractDetailView(DetailView):
    template_name = os.path.join('employees', 'employee', 'contract', 
        'detail.html')
    model = models.Contract


class TerminationCreateView(ContextMixin ,CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    model = models.Termination
    form_class = forms.TerminationForm

    def get_initial(self):
        return {
            'contract': self.kwargs['pk']
            }

class CreateMultipleEmployeesView(FormView):
    template_name = os.path.join('employees', 'employee', 
        'create_multiple.html')
    form_class = forms.CreateMultipleEmployeesForm
    success_url=reverse_lazy('employees:list-employees')

    def form_valid(self, form):
        resp = super().form_valid(form)
        data = json.loads(urllib.parse.unquote(form.cleaned_data['data']))
        
        
        for line in data:
            dob = line['date_of_birth']
            models.Employee.objects.create(
                first_name = line['first_name'],
                last_name = line['last_name'],
                phone = line['phone'],
                address = line['address'],
                email = line['email'],
                date_of_birth = datetime.datetime.strptime(dob, '%Y-%m-%d')
            )
        return resp


class ImportEmployeesView(ContextMixin, FormView):
    extra_context = {
        'title': 'Import Employees from Excel File'
    }
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.ImportEmployeesForm
    success_url=reverse_lazy('employees:list-employees')

    def form_valid(self, form):
        #assumes all suppliers are organizations
        resp = super().form_valid(form)
        def null_buster(arg):
            if not arg:
                return ''
            return arg


        file = form.cleaned_data['file']
        if file.name.endswith('.csv'):
            #process csv 
            pass
        else:
            cols = [
                form.cleaned_data['first_name'],
                form.cleaned_data['last_name'],
                form.cleaned_data['phone'],
                form.cleaned_data['address'],
                form.cleaned_data['email'],
                form.cleaned_data['date_of_birth'],
            ]
            wb = openpyxl.load_workbook(file.file)
            try:
                ws = wb[form.cleaned_data['sheet_name']]
            except:
                ws = wb.active

        
            for row in ws.iter_rows(min_row=form.cleaned_data['start_row'],
                    max_row = form.cleaned_data['end_row'], 
                    max_col=max(cols)):
                dob = row[form.cleaned_data['date_of_birth']-1].value
                if dob:
                    dob = datetime.datetime.strptime(dob, '%d/%m/%Y')
                models.Employee.objects.create(
                    first_name=row[form.cleaned_data['first_name']-1].value,
                    last_name=row[form.cleaned_data['last_name']-1].value,
                    email=null_buster(row[form.cleaned_data['email']-1].value),
                    phone=null_buster(row[form.cleaned_data['phone']-1].value),
                    address=null_buster(
                        row[form.cleaned_data['address']-1].value),
                    date_of_birth=dob,
                )
                
        return resp
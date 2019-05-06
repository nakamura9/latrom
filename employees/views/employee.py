import datetime
import decimal
import json
import os
import urllib

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

from employees import filters, forms, models, serializers

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer

class EmployeeCreateView( ContextMixin, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    form_class = forms.EmployeeForm
    extra_context = {
        'title': 'Create Employee',
        'description': 'Use this form to record employee data. Employee objects can be added to payroll, and have their vacation time managed. They can also be linked to users.'
    }

    def get(self, request, *args, **kwargs):
        num_employees = models.Employee.objects.filter(active=True).count()

        with open('license.json') as f:
            license = json.load(f)
            if num_employees >= license['license']['number_employees'] :
                return HttpResponseRedirect('/base/license-error/features')

            
        return super().get(request, *args, **kwargs)
    

class EmployeeUpdateView( ContextMixin, UpdateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    success_url = reverse_lazy('employees:dashboard')
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
    template_name = os.path.join('employees', 'employee_list.html')
    filterset_class = filters.EmployeeFilter
    paginate_by = 20
    extra_context = {
        'title': 'List of Employees',
        'new_link': reverse_lazy('employees:create-employee')
    }
    queryset = models.Employee.objects.filter(active=True).order_by('first_name')

class EmployeeDetailView( DetailView):
    template_name = os.path.join('employees', 'employee_detail.html')
    model = models.Employee

class EmployeeDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:list-employees')
    model = models.Employee


class PayrollOfficerCreateView( ContextMixin, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.PayrollOfficerForm
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add Payroll Officer',
        'description': 'Payroll officers are employees assigned to manage employee data such as income and vacation time as well as the roles of users within the system.'
    }

class PayrollOfficerUpdateView( ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.PayrollOfficerUpdateForm
    queryset = models.PayrollOfficer.objects.all()
    success_url = reverse_lazy('employees:dashboard')
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
        with open('license.json') as f:
            license = json.load(f)
            if num_users >= license['license']['number_users']:
                return HttpResponseRedirect('/base/license-error/features')
        
        return super().get(request, *args, **kwargs)

class EmployeeUserPasswordResetView( FormView):
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


def remove_employee_user(request, pk=None):
    obj = models.Employee.objects.get(pk=pk)

    if obj.user:
        obj.user = None
        obj.save()
    return HttpResponseRedirect(reverse_lazy('employees:dashboard'))

class DepartmentCreateView(ContextMixin, CreateView):
    template_name = os.path.join('common_data','crispy_create_template.html')
    form_class = forms.DepartmentForm
    success_url = "/employees/"
    extra_context = {
        'title': 'Create New Department'
    }

class DepartmentUpdateView(ContextMixin, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.DepartmentForm
    model = models.Department
    success_url = "/employees/"
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
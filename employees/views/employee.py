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
from common_data.utilities import ExtraContext, ModelViewGroup, apply_style
from common_data.views import PaginationMixin

from employees import filters, forms, models, serializers
from employees.views.util import AdministratorCheckMixin

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')


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


class PayrollOfficerCreateView(AdministratorCheckMixin, ExtraContext, CreateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.PayrollOfficerForm
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add New Payroll Officer'
    }

class PayrollOfficerUpdateView(AdministratorCheckMixin, ExtraContext, UpdateView):
    template_name = CREATE_TEMPLATE
    form_class = forms.PayrollOfficerForm
    queryset = models.PayrollOfficer.objects.all()
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Update Payroll Officer'
    }

class PayrollOfficerListView(AdministratorCheckMixin, ExtraContext, PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'payroll_officer_list.html')
    paginate_by=10
    queryset = models.PayrollOfficer.objects.all()
    filterset_class = filters.PayrollOfficerFilter
    extra_context = {
        'title': 'List of Payroll Officers',
        'new_link': reverse_lazy('employees:payroll-officer-create')
    }


class PayrollOfficerDetailView(AdministratorCheckMixin, DetailView):
    model = models.PayrollOfficer
    template_name = os.path.join('employees', 'payroll_officer_detail.html')

class EmployeeUserCreateView(AdministratorCheckMixin, FormView):
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

class EmployeeUserPasswordResetView(AdministratorCheckMixin, FormView):
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
        obj.user.delete()
    obj.save()
    return HttpResponseRedirect(reverse_lazy('employees:dashboard'))


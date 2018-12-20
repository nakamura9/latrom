import datetime
import decimal
import json
import os
import urllib

from reversion.views import RevisionMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework import viewsets
from django.db.models import Q

from accounting.models import Tax
from common_data.utilities import ExtraContext, ConfigMixin, apply_style
from common_data.views import PaginationMixin

from employees import filters, forms, models, serializers
from employees.views.util import AdministratorCheckMixin
from messaging.models import Notification

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')


class DeductionCreateView(AdministratorCheckMixin, ExtraContext, CreateView):
    form_class = forms.DeductionForm
    template_name = os.path.join('common_data','create_template.html')
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add Deductions For Payroll'
    }

class DeductionUpdateView(AdministratorCheckMixin, ExtraContext, UpdateView):
    form_class = forms.DeductionUpdateForm
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
    form_class = forms.AllowanceUpdateForm
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
    form_class = forms.CommissionUpdateForm
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


class PayGradeCreateView(AdministratorCheckMixin, ExtraContext, CreateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    success_url = reverse_lazy('employees:dashboard')
    extra_context = {
        'title': 'Add Pay Grade',
        'description': 'Use pay grades to group employees on the same income level. Apply commission rules, benefits, deductions and taxes to each unique grade.',
        'related_links': [
            {
                'name': 'Add Commission Rule',
                'url': '/employees/create-commission/'
            },
            {
                'name': 'Add Allowance',
                'url': '/employees/create-allowance/'
            },
            {
                'name': 'Add Deduction',
                'url': '/employees/create-deduction/'
            },
            {
                'name': 'Add Tax',
                'url': '/employees/create-payroll-tax/'
            }
        ] 
    }

class PayGradeUpdateView(AdministratorCheckMixin, RevisionMixin ,ExtraContext, UpdateView):
    form_class = forms.PayGradeForm
    template_name =CREATE_TEMPLATE
    success_url = reverse_lazy('employees:list-pay-grades')
    extra_context = {
        'title': 'Edit existing Pay Grade'
    }
    queryset = models.PayGrade.objects.all()

class PayGradeListView(AdministratorCheckMixin, PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'pay_grade_list.html')
    paginate_by = 10
    queryset =  models.PayGrade.objects.all()
    filterset_class = filters.PayGradeFilter
    extra_context = {
        'title': 'List of Pay grades',
        'new_link': reverse_lazy('employees:create-pay-grade')
    }

class PayGradeDeleteView(AdministratorCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template')
    success_url = reverse_lazy('employees:list-pay-grades')
    model = models.PayGrade

class PayslipView(AdministratorCheckMixin, ConfigMixin, DetailView):
    template_name = os.path.join('employees', 'payslip', 'detail.html')
    model= models.Payslip
    
class PayslipListView(AdministratorCheckMixin, 
        ExtraContext, 
        PaginationMixin, 
        FilterView):
    filterset_class = filters.PayslipFilter
    template_name = os.path.join('employees', 'payslip', 'list.html')
    paginate_by = 10
    extra_context = {
        'title': 'List of Payslips',
        'new_link': '/employees/manual-config'
    }

    def get_queryset(self):
        return models.Payslip.objects.all().order_by('start_period')
  
class PayslipVerificationView(AdministratorCheckMixin, 
        ConfigMixin,
        DetailView):
    template_name = os.path.join('employees', 'payslip', 'verify.html')
    model= models.Payslip

class PayslipDeleteView(AdministratorCheckMixin, DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.Payslip


def verify_payslip(request, pk=None):
    slip = get_object_or_404(models.Payslip, pk=pk)
    slip.status = 'verified'
    slip.save()

    return HttpResponseRedirect('/employees/list-pay-slips')

def execute_payroll(request):
    slips = models.Payslip.objects.filter(status='verified')
    for slip in slips:
        slip.create_entry()

    messages.info(request, '%d payslips have been paid' % slips.count())
    return HttpResponseRedirect('/employees/')

class BulkPayslipVerificationView(AdministratorCheckMixin, FormView):
    pass

class PayslipViewset(viewsets.ModelViewSet):
    queryset = models.Payslip.objects.all()
    serializer_class = serializers.PayslipSerializer

class PayrollTaxCreateView(AdministratorCheckMixin, CreateView):
    template_name = os.path.join('employees','payroll_tax', 'create.html')
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

class PayrollTaxDetailView(AdministratorCheckMixin, DetailView):
    template_name = os.path.join('employees', 'payroll_tax', 'detail.html')
    model = models.PayrollTax

class PayrollTaxListView(ExtraContext, AdministratorCheckMixin, PaginationMixin,
        FilterView):
    template_name = os.path.join('employees', 'payroll_tax', 'list.html')
    queryset = models.PayrollTax.objects.all()
    extra_context = {
        'title': 'Payroll Tax List',
        'new_link': reverse_lazy('employees:create-payroll-tax')
    }
    filterset_class = filters.PayrollTaxFilter


class PayrollTaxDeleteView(DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.PayrollTax
    success_url = reverse_lazy('employees:dashboard')

def run_payroll(request):
    pass

class ManualPayrollConfig(AdministratorCheckMixin, FormView):
    template_name = os.path.join('employees', 'manual_config.html')
    form_class = forms.PayrollForm
    success_url = reverse_lazy('employees:dashboard')

    def get(self, request):
        resp = super().get(request)
        if not models.EmployeesSettings.objects.first().payroll_officer:
            messages.info(request, 'Please assign a payroll officer in the automated configuration page before running this service.')

        return resp

    def form_valid(self, form):
        resp = super().form_valid(form)
        service = ManualPayrollService(form.cleaned_data)
        service.run()


        return resp

class ManualPayrollService(object):
    def __init__(self, form_data):
        self.settings = models.EmployeesSettings.objects.first()
        self.employees = form_data['employees']
        self.start = form_data['start_period']
        self.end = form_data['end_period']
        self.month = self.end.month
        self.year = self.end.year

    def run(self):
        print('running manual payroll service')
        for employee in self.employees:
            if self.check_existing_payslip(employee):
                Notification.objects.create(
                    user=self.settings.payroll_officer.user,
                    title="Payroll",
                    message="""
                    THis notification message was generated by the payroll system.
                    The employee {} already has a payslip for the period specified for the manual payslip, please revise their time sheet or paygrade to make changes 
                    """.format(str(employee)),
                    action=""
                )
            elif employee.uses_timesheet:
                self.generate_wage_payslip(employee)
            else:
                self.generate_salaried_payslip(employee)


    def check_existing_payslip(self, employee):
        slips = models.Payslip.objects.filter(Q(employee=employee) & Q(Q(
            Q(start_period__lte=self.start) & 
            Q(end_period__gte=self.start)   
        ) | Q(
            Q(start_period__lte=self.end) & 
            Q(end_period__gte=self.end) 
        )))
        
        if slips.count() > 0:
            return True

        return False


    def generate_salaried_payslip(self, employee):
        models.Payslip.objects.create(
                start_period = self.start,
                end_period = self.end,
                employee = employee,
                normal_hours = 0,
                overtime_one_hours = 0,
                overtime_two_hours = 0,
                pay_roll_id = self.settings.payroll_counter
            )

    def generate_wage_payslip(self, employee):
        NOW = datetime.datetime.now()
        sheet = self.get_employee_timesheet(employee)
        if sheet:
            if sheet.complete:
                models.Payslip.objects.create(
                    start_period = self.start,
                    end_period = self.end,
                    employee = employee,
                    normal_hours = (sheet.normal_hours.seconds / 3600),
                    overtime_one_hours = (sheet.overtime.seconds / 3600),
                    overtime_two_hours = 0,
                    pay_roll_id = self.settings.payroll_counter
                )
            else:
                Notification.objects.create(
                    user = self.settings.payroll_officer.user,
                    title = 'Payroll',
                    message = """This notification message was generated by the payroll system.  
                    The employee {} does not have a complete timesheet and therefore the payslip generation
                    process could not complete. Please complete the timesheet then create a manual payslip from the 
                    recorded data.""".format(str(employee)),
                    action = reverse_lazy('employees:timesheet-update', kwargs={'pk': employee.pk})
                )
        else:
                Notification.objects.create(
                    user = self.settings.payroll_officer.user,
                    title = 'Payroll',
                    message = """This notification message was generated by the payroll system.  
                    The employee {} does not have a timesheet for the current pay period and therefore the payslip generation
                    process could not complete. Please create a new timesheet then create a manual payslip from the 
                    recorded data.""".format(str(employee)),
                    action = reverse_lazy('employees:timesheet-create')
                )
        

    def get_employee_timesheet(self, employee):
        sheet_filters = Q(
            Q(employee=employee) &
            Q(month=self.month) &
            Q(year=self.year)
        )
        if models.EmployeeTimeSheet.objects.filter(sheet_filters).exists():
            return models.EmployeeTimeSheet.objects.get(sheet_filters)

        return None

    
        
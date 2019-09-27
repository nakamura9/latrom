import datetime
import decimal
import json
import os
import urllib

from reversion.views import RevisionMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import (CreateView, DeleteView, FormView,
                                       UpdateView)
from django_filters.views import FilterView
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from django.db.models import Q

from accounting.models import Tax
from common_data.utilities import ContextMixin, ConfigMixin, apply_style
from common_data.views import PaginationMixin, PDFDetailView
from accounting.views import ProfitAndLossReport

from employees import filters, forms, models, serializers
from planner.models import Event

CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')


class DeductionListView(ContextMixin, ListView):
    template_name = os.path.join('employees', 'deductions', 'list.html')
    extra_context = {
        'title': 'List of Payroll Deductions',
        'new_link': '/employees/create-deduction'
    }
    paginate_by = 10
    queryset = models.Deduction.objects.filter(active=True)

class DeductionDetailView(DetailView):
    template_name = os.path.join('employees', 'deductions', 'detail.html')
    model = models.Deduction

class DeductionCreateView( ContextMixin, CreateView):
    form_class = forms.DeductionForm
    template_name = os.path.join('common_data','crispy_create_template.html')
    extra_context = {
        'title': 'Add Deductions For Payroll'
    }

    def get_initial(self):
        return {
            'account_paid_into': 5008
        }

class DeductionUpdateView( ContextMixin, UpdateView):
    form_class = forms.DeductionUpdateForm
    model = models.Deduction
    template_name = os.path.join('common_data','create_template.html')
    extra_context = {
        'title': 'Update existing deduction'
    }

class DeductionDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:dashboard')
    model = models.Deduction


class AllowanceListView(ContextMixin, ListView):
    template_name = os.path.join('employees', 'benefits', 'list.html')
    queryset = models.Allowance.objects.filter(active=True)
    paginate_by = 20
    extra_context = {
        'title': 'Payroll Benefits List',
        'new_link': '/employees/create-allowance'
    }

class AllowanceDetailView(DetailView):
    template_name = os.path.join('employees', 'benefits', 'detail.html')
    model = models.Allowance

class AllowanceCreateView( ContextMixin, CreateView):
    form_class = forms.AllowanceForm
    template_name = os.path.join('common_data','create_template.html')
    extra_context = {
        'title': 'Create New Allowance '
    }

class AllowanceUpdateView( ContextMixin, UpdateView):
    form_class = forms.AllowanceUpdateForm
    model = models.Allowance
    template_name = os.path.join('common_data','create_template.html')
    extra_context = {
        'title': 'Edit Existing Allowance '
    }

class AllowanceDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:dashboard')
    model = models.Allowance

class CommissionListView(ContextMixin, ListView):
    template_name = os.path.join('employees', 'commissions', 'list.html')
    model = models.CommissionRule
    paginate_by=10
    extra_context = {
        'title': 'List of Commission Rules',
        'new_link': '/employees/create-commission'
    }

class CommissionDetailView(DetailView):
    template_name = os.path.join('employees', 'commissions', 'detail.html')
    model = models.CommissionRule

class CommissionCreateView( ContextMixin, CreateView):
    form_class = forms.CommissionForm
    template_name = os.path.join('common_data','create_template.html')
    extra_context = {
        'title': 'Create Commission Rule'
    }

class CommissionUpdateView( ContextMixin, UpdateView):
    form_class = forms.CommissionUpdateForm
    model = models.CommissionRule
    template_name = os.path.join('common_data','create_template.html')
    extra_context = {
        'title': 'Edit Existing Commission Rule'
    }

class CommissionDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = reverse_lazy('employees:dashboard')
    model = models.CommissionRule


class PayGradeCreateView( ContextMixin, CreateView):
    form_class = forms.PayGradeForm
    template_name = os.path.join('common_data', 'crispy_create_template.html')
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
        ],
        'box_array': 
            urllib.parse.quote(json.dumps([{
                "model": "commissionrule",
                "app": "employees",
                "id": "id_commission",
            }]))
    }

class PayGradeDetailView(DetailView):
    model = models.PayGrade
    template_name=os.path.join('employees', 'paygrade_detail.html')

class PayGradeUpdateView( RevisionMixin ,ContextMixin, UpdateView):
    form_class = forms.PayGradeForm
    template_name =os.path.join('common_data', 'crispy_create_template.html')
    extra_context = {
        'title': 'Edit existing Pay Grade'
    }
    queryset = models.PayGrade.objects.all()

class PayGradeListView( PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'pay_grade_list.html')
    paginate_by = 20
    queryset =  models.PayGrade.objects.all()
    filterset_class = filters.PayGradeFilter
    extra_context = {
        'title': 'List of Pay grades',
        'new_link': reverse_lazy('employees:create-pay-grade')
    }

class PayGradeDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template')
    success_url = reverse_lazy('employees:list-pay-grades')
    model = models.PayGrade

class PayslipView(ContextMixin, ConfigMixin, DetailView):
    template_name = os.path.join('employees', 'payslip', 'detail.html')
    model= models.Payslip
    extra_context = {
        'pdf_link': True
    }

class BasicPayslipView(ContextMixin, ConfigMixin, DetailView):
    template_name = os.path.join('employees', 'payslip', 'basic.html')
    model= models.Payslip
    extra_context = {
        'pdf_link': True
    }

class BasicPayslipPDFView(ConfigMixin, PDFDetailView):
    template_name = os.path.join('employees', 'payslip', 'basic.html')
    file_name="payslip.pdf"
    model = models.Payslip
    
class PayslipListView( 
        ContextMixin, 
        PaginationMixin, 
        FilterView):
    filterset_class = filters.PayslipFilter
    template_name = os.path.join('employees', 'payslip', 'list.html')
    paginate_by = 20
    extra_context = {
        'title': 'List of Payslips',
        'new_link': '/employees/manual-config',
        'action_list': [
            {
                'icon': 'list-ol',
                'label': 'View outstanding Payslips',
                'link': '/employees/outstanding-payslips'
            }
        ]
    }

    def get_queryset(self):
        return models.Payslip.objects.all().order_by('start_period').reverse()


class EmployeePayslipListView( 
        ContextMixin, 
        PaginationMixin, 
        FilterView):
    filterset_class = filters.PayslipFilter
    template_name = os.path.join('employees', 'portal', 'payslip_list.html')
    paginate_by = 20
    extra_context = {
        'title': 'List of Payslips',
    }

    def get_queryset(self):
        employee = models.Employee.objects.get(pk=self.kwargs['pk'])
        return models.Payslip.objects.filter(employee=employee).order_by('start_period').reverse()
  
class PayslipVerificationView( 
        ConfigMixin,
        DetailView):
    template_name = os.path.join('employees', 'payslip', 'verify.html')
    model= models.Payslip

class PayslipDeleteView( DeleteView):
    template_name = os.path.join('common_data', 'delete_template.html')
    model = models.Payslip
    success_url = '/employees/'


def verify_payslip(request, pk=None):
    slip = get_object_or_404(models.Payslip, pk=pk)
    slip.status = 'verified'
    slip.save()
    slip.create_verified_entry()

    return HttpResponseRedirect('/employees/list-pay-slips')

def process_payment(request, pk=None):
    slip = get_object_or_404(models.Payslip, pk=pk)
    
    slip.create_entry()

    return HttpResponseRedirect('/employees/list-pay-slips')

def execute_payroll(request):
    # last thirty days
    today = datetime.date.today()
    settings = models.EmployeesSettings.objects.first()
    p_and_l = ProfitAndLossReport.common_context({}, today - datetime.timedelta(days=30), today)

    if p_and_l['net_profit'] < 0 and settings.salary_follows_profits:
        messages.info(request, 'Payroll settings prevent payslips from being paid out')
        return HttpResponseRedirect('/employees/')    
    
    slips = models.Payslip.objects.filter(status='verified')

    for slip in slips:
        slip.create_entry()

    messages.info(request, '%d payslips have been paid' % slips.count())
    return HttpResponseRedirect('/employees/')

class BulkPayslipVerificationView( FormView):
    pass

class PayslipViewset(viewsets.ModelViewSet):
    queryset = models.Payslip.objects.all()
    serializer_class = serializers.PayslipSerializer

class PayrollTaxCreateView( CreateView):
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

class PayrollTaxUpdateView( ContextMixin, UpdateView):
    template_name = os.path.join('common_data','create_template.html')
    form_class = forms.PayrollTaxUpdateForm
    success_url = reverse_lazy('employees:dashboard')
    model = models.PayrollTax
    extra_context = {
        'title': 'Update Payroll Tax Object'
    }

class PayrollTaxDetailView( DetailView):
    template_name = os.path.join('employees', 'payroll_tax', 'detail.html')
    model = models.PayrollTax

class PayrollTaxListView(ContextMixin,  PaginationMixin,
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


class ManualPayrollConfig( FormView):
    template_name = os.path.join('employees', 'manual_config.html')
    form_class = forms.PayrollForm
    success_url = reverse_lazy('employees:dashboard')

    def form_valid(self, form):
        resp = super().form_valid(form)
        service = ManualPayrollService(form.cleaned_data, self.request)
        service.run()


        return resp

class ManualPayrollService(object):
    def __init__(self, form_data, request):
        self.settings = models.EmployeesSettings.objects.first()
        self.employees = form_data['employees']
        self.officer = form_data['payroll_officer']
        self.start = form_data['start_period']
        self.end = form_data['end_period']
        self.month = self.end.month
        self.year = self.end.year
        self.request = request

    def run(self):
        print('running manual payroll service')
        payslip_count = 0
        for employee in self.employees:
            if not employee.pay_grade:
                messages.info(
                    self.request,
                    """
                    The employee {} has no paygrade and therefore
                    cannot have a payslip generated.
                    """.format(str(employee))
                )
                continue

            elif self.check_existing_payslip(employee):
                messages.info(self.request,"""
                    The employee {} already has a payslip for the period specified for the manual payslip, please revise their time sheet or paygrade to make changes 
                    """.format(str(employee))
                )
                continue

            elif employee.uses_timesheet:
                self.generate_wage_payslip(employee)
                payslip_count += 1
            else:
                self.generate_salaried_payslip(employee)
                payslip_count += 1

                
            self.adjust_leave_days(employee)
            messages.info(self.request, f'{payslip_count} payslips generated')

    def check_existing_payslip(self, employee):
        return models.Payslip.objects.filter(Q(employee=employee) & Q(Q(
            Q(start_period__lte=self.start) & 
            Q(end_period__gte=self.start)   
        ) | Q(
            Q(start_period__lte=self.end) & 
            Q(end_period__gte=self.end) 
        ))).exists()
        

    def generate_salaried_payslip(self, employee):
        return models.Payslip.objects.create(
                start_period = self.start,
                end_period = self.end,
                employee = employee,
                normal_hours = 0,
                overtime_one_hours = 0,
                overtime_two_hours = 0,
                pay_roll_id = self.settings.payroll_counter
            )

    def generate_wage_payslip(self, employee):
        sheet = self.get_employee_timesheet(employee)
        if sheet:
            if sheet.complete:
                return models.Payslip.objects.create(
                    start_period = self.start,
                    end_period = self.end,
                    employee = employee,
                    normal_hours = (sheet.normal_hours.seconds / 3600),
                    overtime_one_hours = (sheet.overtime.seconds / 3600),
                    overtime_two_hours = 0,
                    pay_roll_id = self.settings.payroll_counter
                )
            else:
                messages.info(self.request,
                     """  
                    The employee {} does not have a complete timesheet and therefore the payslip generation
                    process could not complete. Please complete the timesheet then create a manual payslip from the 
                    recorded data.""".format(str(employee)))
                return None
        else:
                messages.info(self.request,
                 """  
                    The employee {} does not have a timesheet for the current pay period and therefore the payslip generation
                    process could not complete. Please create a new timesheet then create a manual payslip from the 
                    recorded data.""".format(str(employee)
                ))
                return None
        

    def get_employee_timesheet(self, employee):
        sheet_filters = Q(
            Q(employee=employee) &
            Q(month=self.month) &
            Q(year=self.year)
        )
        if models.EmployeeTimeSheet.objects.filter(sheet_filters).exists():
            return models.EmployeeTimeSheet.objects.get(sheet_filters)

        return None

    def adjust_leave_days(self, employee):
        if employee.last_leave_day_increment is None  or \
                (self.start -  employee.last_leave_day_increment).days >= 30:
            employee.leave_days += employee.pay_grade.monthly_leave_days
            employee.last_leave_day_increment = self.start
            employee.save()

        for leave in models.Leave.objects.filter(
                Q(recorded=False) &
                Q(status=1) &
                Q(employee=employee)):
        
            if leave.start_date <= self.end:
                leave.recorded = True
                leave.employee.leave_days -= leave.duration
                leave.save()
                leave.employee.save()

class PayslipPDFView(ConfigMixin, PDFDetailView):
    template_name = os.path.join('employees', 'payslip', 'detail.html')
    file_name="payslip.pdf"
    model = models.Payslip

class PayrollDateListView(ContextMixin, PaginationMixin, FilterView):
    template_name = os.path.join('employees', 'payroll_date_list.html')
    filterset_class = filters.PayrollDateFilter
    queryset = models.PayrollDate.objects.all()
    paginate_by = 20

    extra_context = {
        'title': 'List of Payroll Dates',
        'new_link': '/employees/payroll-date/create'
    }

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

class PayrollDateUpdateView(ContextMixin, UpdateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.PayrollDateForm
    model = models.PayrollDate
    extra_context = {
        'title': 'Update Payroll Date Features'
    }

class PayrollDateDeleteView(DeleteView):
    model = models.PayrollDate
    template_name = os.path.join('common_data', 'delete_template.html')
    success_url = "/employees"

class PayrollDateDetailView(DetailView):
    model = models.PayrollDate
    template_name = os.path.join('employees', 'payroll_date_detail.html')

class CreatePayrollDateView(ContextMixin, CreateView):
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    form_class = forms.PayrollDateForm
    extra_context = {
        'title': 'Create Payroll Date'
    }

    def post(self, request, *args, **kwargs):
        resp = super().post(self, request, *args, **kwargs)

        if not self.object:
            return resp

        today = datetime.date.today()

        #the app always has at least one payroll officer 
        settings = models.EmployeesSettings.objects.first()
        if not settings.payroll_officer:
            officer = models.PayrollOfficer.objects.first()
            if not officer.employee.user:
                user = User.objects.create_user(
                    officer.employee.first_name, password='1234')
                officer.employee.user = user
                officer.save()
            settings.payroll_officer = officer 
            settings.save()

        
            
        Event.objects.create(
            date = datetime.date(today.year, today.month, self.object.date),
            reminder = datetime.timedelta(days=1),
            start_time = datetime.time(8,0),
            description= f"Payroll Schedule date {self.object.date}"
            f"{self.object.date_suffix} of this month for employees in "
            f"{', '.join([str(i) for i in self.object.departments.all()])}" f"departments. And employees with"
            f" {', '.join([str(i) for i in self.object.pay_grades.all()])} ."
            f"Total Employees Included:{self.object.number_of_employees}",
            repeat=3,#monthly
            repeat_active=True,
            label="Payroll Date",
            icon="calendar",
            owner=models.EmployeesSettings.objects.first().payroll_officer.employee.user
        )
        
        return resp

    def get_initial(self):
        return {
            'schedule': 1
        }

class OutstandingPayslipsView(ContextMixin, FormView):
    form_class = forms.OutstandingPayslipsForm
    success_url = reverse_lazy('employees:list-pay-slips')
    template_name = os.path.join('common_data', 'crispy_create_template.html')
    extra_context = {
        'title': 'List of outstanding payslips'
    }

    def form_valid(self, form):
        resp = super().form_valid(form)
        
        data = json.loads(urllib.parse.unquote(form.cleaned_data['data']))

        for line in data:
            print(line)
            slip = models.Payslip.objects.get(pk=line['id'])
            if line['status'] != '' and slip.status != 'paid' and \
                    line['status'] != slip.status:
                slip.status = line['status']
                slip.save()
                if line['status'] == 'paid':
                    slip.create_entry()

        return resp

class OutstandingSlipsAPIView(ListAPIView):
    serializer_class = serializers.PayslipSerializer
    queryset = models.Payslip.objects.exclude(status='paid')
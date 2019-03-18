import os
import datetime
from dateutil import *
from messaging.models import Notification

from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.models import User
from common_data.utilities import ContextMixin

from employees import forms, models
from .employee import *
from .leave import *
from .payroll import *
from accounting.models import Account
from .timesheets import *

#constants
CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class DashBoard( ContextMixin, TemplateView):
    template_name = os.path.join('employees', 'dashboard.html')
    extra_context = {
        'employees': models.Employee.objects.all()
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        TODAY = datetime.date.today()
        context['calendar_url'] = '/employees/leave-calendar/month/{}'.format(
            datetime.date.today().strftime('%Y/%m'))
        context['employees'] = models.Employee.objects.filter(
            active=True).count()
        context['users'] = User.objects.all().count()
        context['leaves'] = sum([i.duration for i in  
            models.Leave.objects.filter(
                Q(start_date__gte=TODAY) &
                Q(status=1))])
        context['slips'] = models.Payslip.objects.filter(Q(status="draft") | Q(
            status="verified")).count()
        context['unpaid_wages'] = sum([i.gross_pay for i in \
            models.Payslip.objects.filter(Q(status="verified"))])


        context['tax'] = Account.objects.get(pk=5010).balance
        return context


    def get(self, request):
        service = AutomatedPayrollService()
        service.run()
        return super().get(request)

class PayrollConfig( ContextMixin, UpdateView):
    model = models.EmployeesSettings
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy("employees:dashboard")
    form_class = forms.EmployeesSettingsForm
    extra_context = {
        'title': 'Configure automated Payroll'
    }
        

class AutomatedPayrollService(object):
    def __init__(self):
        self.settings = models.EmployeesSettings.objects.first()
        self.TODAY  = datetime.date.today()
        self.pay_dates = [
            self.settings.payroll_date_one,
            self.settings.payroll_date_two,
            self.settings.payroll_date_three,
            self.settings.payroll_date_four
        ]

        self.start = None
        if self.settings.last_payroll_date:
            self.start = self.settings.last_payroll_date
        else:
            if self.settings.payroll_cycle == "monthly":
                self.start = self.TODAY - relativedelta.relativedelta(months=1)
            if self.settings.payroll_cycle == "bi-monthly":
                self.start = self.TODAY - datetime.timedelta(days=14)
            else:
                self.start = self.TODAY - datetime.timedelta(days=7)

    def run(self):
        print("running payroll service")
        if self.TODAY.day in self.pay_dates and \
                self.TODAY != self.settings.last_payroll_date:
            payroll_id = self.settings.payroll_counter + 1
            
            self.run_salaries_payroll(payroll_id)
            self.run_wages_payroll(payroll_id)
            
            self.settings.last_payroll_date = self.TODAY
            self.settings.payroll_counter = payroll_id
            self.settings.save()

        self.adjust_leave_days()
            
            
    def run_salaries_payroll(self, payroll_id):
        salaried = models.Employee.objects.filter(
            active=True, 
            uses_timesheet=False
            )
        for employee in salaried:
            

            models.Payslip.objects.create(
                start_period = self.start,
                end_period = self.TODAY,
                employee = employee,
                normal_hours = 0,
                overtime_one_hours = 0,
                overtime_two_hours = 0,
                pay_roll_id = payroll_id
            )

    def run_wages_payroll(self, payroll_id):
        wage_earners = models.Employee.objects.filter(
                active=True, 
                uses_timesheet=True
            )

        for employee in wage_earners:
            sheet = self.get_employee_timesheet(employee)
            if sheet:
                if sheet.complete:
                    models.Payslip.objects.create(
                        start_period = self.start,
                        end_period = self.TODAY,
                        employee = employee,
                        normal_hours = sheet.normal_hours.seconds / 3600,
                        overtime_one_hours = sheet.overtime.seconds / 3600,
                        overtime_two_hours = 0,
                        pay_roll_id = payroll_id
                    )
                else:
                    Notification.objects.create(
                        user = self.settings.payroll_officer.user,
                        title = 'Payroll',
                        message = """This notification message was generated by the payroll system.  
                        The employee {} does not have a complete timesheet and therefore the payslip generation
                        process could not complete. Please complete the timesheet then create a manual payslip from the 
                        recorded data.""",
                        action = reverse_lazy('employees:timesheet-update', kwargs={'pk': employee.pk})
                    )
            else:
                 Notification.objects.create(
                     user = self.settings.payroll_officer.user,
                        title = 'Payroll',
                        message = """This notification message was generated by the payroll system.  
                        The employee {} does not have a timesheet for the current pay period and therefore the payslip generation
                        process could not complete. Please create a new timesheet then create a manual payslip from the 
                        recorded data.""",
                        action = reverse_lazy('employees:timesheet-create')
                    )
        

    def get_employee_timesheet(self, employee):
        sheet_filters = Q(
            Q(employee=employee) &
            Q(month=self.TODAY.month) &
            Q(year=self.TODAY.year)
        )
        if models.EmployeeTimeSheet.objects.filter(sheet_filters).exists():
            return models.EmployeeTimeSheet.objects.get(sheet_filters)

        return None

    def adjust_leave_days(self):
        for employee in models.Employee.objects.all():
            if employee.last_leave_day_increment is None  or \
                    (self.TODAY -  employee.last_leave_day_increment).days > 30:
                employee.leave_days += employee.pay_grade.monthly_leave_days
                employee.last_leave_day_increment = self.TODAY
                employee.save()

        for leave in models.Leave.objects.filter(
                Q(recorded=False) &
                Q(status=1)):
        
            if leave.start_date <= self.TODAY:
                leave.recorded = True
                leave.employee.leave_days -= leave.duration
                leave.save()
                leave.employee.save()

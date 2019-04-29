import os
import datetime
from dateutil import *
from dateutil.relativedelta import relativedelta
from messaging.models import Notification
from django.contrib import messages

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
from .employee_portal import *
from employees.views.dash_plotters import employee_roles_chart
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from background_task import background

#constants
CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

@background(schedule=5)
def print_hello():
    print('hello world')

class DashBoard( ContextMixin, TemplateView):
    template_name = os.path.join('employees', 'dashboard.html')
    extra_context = {
        'employees': models.Employee.objects.all()
    }

    def get(self, request, *args, **kwargs):
        config = models.EmployeesSettings.objects.first()
        #print_hello()
        if config is None:

            config = models.EmployeesSettings.objects.create(is_configured = False)
        
        print(config.is_configured)
        if config.is_configured:
            service = AutomatedPayrollService()
            try:
                service.run()
            except PayrollException:
                messages.info(request, 'The payroll system does not have any payroll dates loaded. Please enter suitable dates for the system to automatically generate payslips')
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy('employees:config-wizard'))

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
        context['graph'] = employee_roles_chart().render(is_unicode=True)


        context['tax'] = Account.objects.get(pk=5010).balance
        return context


class PayrollConfig( ContextMixin, UpdateView):
    model = models.EmployeesSettings
    template_name = CREATE_TEMPLATE
    success_url = reverse_lazy("employees:dashboard")
    form_class = forms.EmployeesSettingsForm
    extra_context = {
        'title': 'Configure automated Payroll'
    }
        

class PayrollException(Exception):
    pass

class AutomatedPayrollService(object):
    def __init__(self):
        self.settings = models.EmployeesSettings.objects.first()
        self.TODAY  = datetime.date.today()

    def run(self):
        print("running payroll service")
        schedule = models.PayrollSchedule.objects.first()
        if schedule.payrolldate_set.all().count() == 0:
            raise PayrollException('The schedule has no payroll dates')

        if any([self.TODAY.day == i.date \
                for i in schedule.payrolldate_set.all()]):
            
            payroll_date = models.PayrollDate.objects.get(date=self.TODAY.day)
            payroll_id = self.settings.payroll_counter + 1
            self.settings.last_payroll_date = self.TODAY
            self.settings.payroll_counter = payroll_id
            self.settings.save()

            employees = payroll_date.all_employees

            for employee in employees:
                if employee.uses_timesheet:
                    sheet = self.get_employee_timesheet(employee)
                    if sheet and sheet.complete:
                        models.Payslip.objects.create(
                            start_period = self.get_start_date(employee),
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
                    models.Payslip.objects.create(
                        start_period = self.get_start_date(employee),
                        end_period = self.TODAY,
                        employee = employee,
                        normal_hours = 0,
                        overtime_one_hours = 0,
                        overtime_two_hours = 0,
                        pay_roll_id = payroll_id
                    )
            
            self.adjust_leave_days()

    def get_employee_timesheet(self, employee):
        sheet_filters = Q(
            Q(employee=employee) &
            Q(month=self.TODAY.month) &
            Q(year=self.TODAY.year)
        )
        if models.EmployeeTimeSheet.objects.filter(sheet_filters).exists():
            return models.EmployeeTimeSheet.objects.get(sheet_filters)

        return None

    def get_start_date(self, employee):
        mapping = {
            0: datetime.timedelta(days=7),
            1: relativedelta(weeks=2),
            2: relativedelta(months=1)
        }
        return self.TODAY - mapping[employee.pay_grade.pay_frequency]


    def adjust_leave_days(self):
        for employee in models.Employee.objects.all():
            if employee.last_leave_day_increment is None  or \
                    (self.TODAY -  employee.last_leave_day_increment).days > 30:
                employee.increment_leave_days(
                    employee.pay_grade.monthly_leave_days)
                
        for leave in models.Leave.objects.filter(
                Q(recorded=False) &
                Q(status=1)):
        
            if leave.start_date <= self.TODAY:
                leave.recorded = True
                leave.save()
                leave.employee.deduct_leave_days(leave.duration)

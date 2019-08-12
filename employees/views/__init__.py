import os
import datetime
from dateutil import *
from dateutil.relativedelta import relativedelta
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
from .reports import *
from accounting.models import Account
from .timesheets import *
from .employee_portal import *
from employees.views.dash_plotters import employee_roles_chart
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from background_task import background

#constants
CREATE_TEMPLATE = os.path.join('common_data', 'create_template.html')

class Dashboard(ContextMixin, TemplateView):
    template_name = os.path.join('employees', 'dashboard.html')
    extra_context = {
        'employees': models.Employee.objects.all()
    }

    def get(self, request, *args, **kwargs):
        config = models.EmployeesSettings.objects.first()
        if config is None:

            config = models.EmployeesSettings.objects.create(is_configured = False)
        
        if config.is_configured:
            ungraded = models.Employee.objects.filter(pay_grade__isnull=True).count()
            if ungraded > 0:
                messages.info(request, f'{ungraded} employees have no paygrades, please review the employees and assign paygrades to them for payroll to work')

            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy('employees:config-wizard'))


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        TODAY = datetime.date.today()
        context['calendar_url'] = '/employees/leave-calendar/month/{}'.format(
            datetime.date.today().strftime('%Y/%m'))
        return context

class AsyncDashboard(ContextMixin, TemplateView):
    template_name = os.path.join('employees', 'async_dashboard.html')
    
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
        


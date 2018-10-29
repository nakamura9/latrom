import os


from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView
from common_data.utilities import ExtraContext

from employees import forms, models
from .employee import *
from .payroll import *
from .timesheets import *
from employees.views.util import AdministratorCheckMixin 
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


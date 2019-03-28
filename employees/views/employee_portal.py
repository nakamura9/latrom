from django.views.generic import TemplateView, DetailView
from django.views.generic.edit import FormView
from employees.models import Employee
from employees.forms import EmployeeAuthenticateForm
import os 
import datetime

class EmployeePortalLogin(FormView):
    form_class = EmployeeAuthenticateForm
    template_name = os.path.join('employees', 'portal', 'login.html')
    
    def get_success_url(self):
        return f'/employees/portal/dashboard/{self.request.POST["employee"]}'
        


class EmployeeDashboard(DetailView):
    template_name = os.path.join('employees', 'portal', 'dashboard.html')
    model = Employee

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['calendar_url'] = '/employees/leave-calendar/month/{}'.format(
            datetime.date.today().strftime('%Y/%m'))
        return context
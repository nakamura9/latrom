import datetime
import os 
from django.views.generic import TemplateView
from employees.models import Employee, Leave
from common_data.utilities import (ConfigMixin, 
                                    ContextMixin,
                                    PeriodReportMixin)
from wkhtmltopdf.views import PDFTemplateView
from common_data.forms import PeriodReportForm



class EmployeeAttendanceReport(ConfigMixin, TemplateView):
    template_name = os.path.join('employees', 
                                 'reports', 
                                 'attendance',
                                 'report.html')

    @staticmethod
    def common_context():
        context = {}
        context["date"] = datetime.date.today()
        context['days'] = list(range(1,32))
        context['employees'] = Employee.objects.filter(uses_timesheet=True)
        context['month'] = datetime.date.today().strftime('%B')
        return context
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pdf_link']=True
        context.update(EmployeeAttendanceReport.common_context())          
        return context

class EmployeeAttendanceReportPDFView(ConfigMixin, PDFTemplateView):
    template_name = EmployeeAttendanceReport.template_name
    file_name="report.pdf"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(EmployeeAttendanceReport.common_context())
        return context
    
'''
#shouldnt need historical leave data
class LeaveReportFormView(ContextMixin, FormView):
    template_name = os.path.join('common_data', 'reports', 'report_template.html')
    form_class = PeriodReportForm
    extra_context = {
        'title': 'Leave Schedule Report'
    }

'''

class LeaveReport(ConfigMixin, TemplateView):
    template_name = os.path.join('employees', 'reports', 'leave.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leave'] = Leave.objects.filter(
            end_date__gte=datetime.date.today(), 
            status=1)
        context['date'] = datetime.date.today()
        context['pdf_link'] =True

        return context
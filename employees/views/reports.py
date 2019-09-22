import datetime
import calendar
import os 
from django.shortcuts import reverse
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from employees.models import Employee, Leave, Payslip
from common_data.utilities import (ConfigMixin, 
                                    MultiPageDocument,
                                    ContextMixin,
                                    PeriodReportMixin,
                                    extract_encoded_period,
                                    extract_period)
from wkhtmltopdf.views import PDFTemplateView
from common_data.forms import PeriodReportForm
from common_data.models import GlobalConfig
from employees import forms



class EmployeeAttendanceReport(ConfigMixin, MultiPageDocument, TemplateView):
    template_name = os.path.join('employees', 
                                 'reports', 
                                 'attendance',
                                 'report.html')

    page_length=30
    
    def get_multipage_queryset(self):
        return Employee.objects.filter(uses_timesheet=True)

    @staticmethod
    def common_context():
        context = {}
        context["date"] = datetime.date.today()
        context['days'] = list(range(1,32))
        context['month'] = datetime.date.today().strftime('%B')
        return context
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pdf_link']=True
        context.update(EmployeeAttendanceReport.common_context())          
        return context

class EmployeeAttendanceReportPDFView(ConfigMixin, 
                                      MultiPageDocument, 
                                      PDFTemplateView):
    template_name = EmployeeAttendanceReport.template_name
    file_name="report.pdf"

    page_length=30
    
    def get_multipage_queryset(self):
        return Employee.objects.filter(uses_timesheet=True)

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

class LeaveReport(ConfigMixin, MultiPageDocument, TemplateView):
    template_name = os.path.join('employees', 'reports', 'leave', 'report.html')
    page_length =20

    def get_multipage_queryset(self):
        return Leave.objects.filter(
            end_date__gte=datetime.date.today(), 
            status=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = datetime.date.today()
        context['pdf_link'] =True

        return context

class LeaveReportPDFView(ConfigMixin, MultiPageDocument, PDFTemplateView):
    template_name = LeaveReport.template_name
    file_name = "report.pdf"
    
    page_length = 20

    def get_multipage_queryset(self):
        return Leave.objects.filter(
            end_date__gte=datetime.date.today(), 
            status=1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['date'] = datetime.date.today()
        

        return context

class PayrollReportFormView(ContextMixin, FormView):
    form_class = PeriodReportForm
    template_name = os.path.join('common_data', 'reports', 'report_template.html')
    
    extra_context = {
        'action': reverse_lazy('employees:payroll-report'),
    }


class PayrollReport(ConfigMixin,
                    MultiPageDocument,
                    PeriodReportMixin,  
                    TemplateView,
                    ):
    template_name = os.path.join('employees', 'reports', 
        'payroll', 'report.html')
    page_length=20

    
    @staticmethod
    def common_multipage_queryset(start, end):
        slips = Payslip.objects.filter(Q(
            Q(status='verified') | Q(status='paid')
            ) & Q(created__date__gte=start)
            & Q(created__date__lte=end))
        employees = {}
        for i in slips:
            employees.setdefault(i.employee.pk , []).append(i)
        
        data = []
        for key in employees.keys():
            employee = Employee.objects.get(pk=key)
            data.append({
                'name': employee.full_name,
                'employee_number': employee.employee_number,
                'id': employee.id_number,
                'grade': employee.pay_grade,
                'taxable_income': sum([i.taxable_gross_pay \
                    for i in employees[key]]),
                'paye': sum([i.total_payroll_taxes for i in employees[key]]),
                'aids': sum([i.aids_levy for i in employees[key]]),
                'total': sum([i.aids_levy_and_taxes for i in employees[key]]),
            })

        return data

    def get_multipage_queryset(self):
        start, end = extract_period(self.request.GET)
        return self.__class__.common_multipage_queryset(start, end)

    @staticmethod
    def common_context(context, start, end):
        context.update({
            'start': start.strftime("%d %B %Y"),
            'end': end.strftime("%d %B %Y"),
            'date': datetime.date.today()
        })
        
        return context


    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        kwargs =  self.request.GET
        start, end = extract_period(kwargs)
        
        context['pdf_link'] = True
        # sales
        return PayrollReport.common_context(context, start, end)

class PayrollPDFReport(ConfigMixin, MultiPageDocument, PDFTemplateView):
    template_name = PayrollReport.template_name
    page_length = PayrollReport.page_length

    def get_multipage_queryset(self):
        start, end = extract_encoded_period(self.kwargs)
        return PayrollReport.common_multipage_queryset(start, end)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        start, end = extract_encoded_period(self.kwargs)
        return context

class NSSAP4Report(TemplateView):
    template_name = os.path.join('employees', 'reports', 'p4',
        'report.html')

    @staticmethod
    def common_context(context, start):
        context['employees'] = [{
            'nps_insurable_earnings': i.get_nps_earnings(start),
            'total_nps': i.total_nps(start),
            'employee': i
            
        } for i in \
             Employee.objects.filter(active=True)] 
        
        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start = datetime.datetime.strptime(self.request.GET['period'], '%b %Y')
        NSSAP4Report.common_context(context, start)
        context['period'] = self.request.GET['period']
        return context 


class ZIMRAP2ReportFormView(ContextMixin, FormView):
    form_class = forms.ZimraReportForm
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    extra_context = {
        'action': '/employees/zimra-p2-report/'
    }
    def get_initial(self):
        today = datetime.date.today()
        return {
            'tax_period': today.strftime('%b %Y')
        }

class NSSAP4ReportFormView(ContextMixin, FormView):
    form_class = forms.NSSAReportForm
    template_name = os.path.join('common_data', 'reports', 
        'report_template.html')
    extra_context = {
        'action': '/employees/nssa-p4-report/'
    }
    def get_initial(self):
        today = datetime.date.today()
        return {
            'period': today.strftime('%b %Y')
        }

class ZIMRAP2Report(ContextMixin, TemplateView):
    template_name = os.path.join('employees', 'reports', 'p2',
        'report.html')
    extra_context = {
        'pdf_link': True
    }

    @staticmethod 
    def common_context(period, address, due):
        period_start = datetime.datetime.strptime(period, 
            '%b %Y').date()
        period_end_date = calendar.monthrange(period_start.year, 
            period_start.month)[1]
        period_end = datetime.date(period_start.year, 
            period_start.month, period_end_date)
        
        slips = Payslip.objects.filter(status__in=['verified', 'paid'],
            created__gte=period_start, created__lte=period_end )
        
        context = {
            'config': GlobalConfig.objects.first(),
            'date_string': datetime.date.today().strftime('%d%m%Y'),
            'employees': Employee.objects.filter(active=True).count(),
            'paye': sum([i.total_payroll_taxes for i in slips]),
            'aids_levy': sum([i.aids_levy for i in slips]),
            'total_remuneration': sum([i.gross_pay for i in slips]),
            'total_tax_due': sum([i.aids_levy_and_taxes for i in slips]),
            'tax_period':period,
            'postal': address,
            'due_date': due,
        }
        
        return context

    def get_context_data(self):
        context = super().get_context_data()
        context.update(ZIMRAP2Report.common_context( 
            self.request.GET['tax_period'],
            self.request.GET['postal_address'],
            self.request.GET['due_date']))
        return context

class ZIMRAP2ReportPDF(PDFTemplateView):
    template_name = os.path.join('employees', 'reports', 'p2',
        'report.html')

    def get_context_data(self):
        return ZIMRAP2Report.common_context( self.request.GET['tax_period'],
            self.request.GET['postal_address'],
            self.request.GET['due_date'])


class NSSAP4ReportPDF(PDFTemplateView):
    template_name = os.path.join('employees', 'reports', 'p4',
        'report.html')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start = datetime.datetime.strptime(self.kwargs['period'], '%b %Y')
        NSSAP4Report.common_context(context, start)
        context['period'] = self.kwargs['period']

        return context
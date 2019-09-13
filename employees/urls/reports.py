from django.urls import path
from employees.views import *

report_urls = [
    path('employee-attendance', EmployeeAttendanceReport.as_view(), 
        name='employee-attendance'),
    path('employee-attendance-pdf', EmployeeAttendanceReportPDFView.as_view(), 
        name='employee-attendance-pdf'),
    path('leave-report', LeaveReport.as_view(), 
        name='leave-report'),
    path('leave-report-pdf', LeaveReportPDFView.as_view(), 
        name='leave-report-pdf'),
    path('payroll-report', PayrollReport.as_view(), 
        name='payroll-report'),
    path('payroll-report-pdf/<str:start>/<str:end>/', 
        PayrollPDFReport.as_view(), 
        name='payroll-report-pdf'),
    path('payroll-report-form', PayrollReportFormView.as_view(), 
        name='payroll-report-form'),
    path('nssa-p4-report', NSSAP4Report.as_view(), 
        name='nssa-p4-report'),
    path('zimra-p2-report/', ZIMRAP2Report.as_view(), 
        name='zimra-p2-report'),
    path('zimra-p2-pdf-report/', ZIMRAP2ReportPDF.as_view(), 
        name='zimra-p2-pdf-report'),
    path('zimra-p2-report-form', ZIMRAP2ReportFormView.as_view(), 
        name='zimra-p2-report-form')
]
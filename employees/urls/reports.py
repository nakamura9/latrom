from django.urls import path
from employees.views import *

report_urls = [
    path('employee-attendance', EmployeeAttendanceReport.as_view(), 
        name='employee-attendance'),
    path('employee-attendance-pdf', EmployeeAttendanceReportPDFView.as_view(), 
        name='employee-attendance-pdf'),
    path('leave-report', LeaveReport.as_view(), 
        name='leave-report'),
]
from django.urls import re_path, path
from rest_framework import routers

from . import views

employee_router = routers.DefaultRouter()
employee_router.register(r'^api/employee', views.EmployeeViewSet)

department_router = routers.DefaultRouter()
department_router.register(r'^api/department', views.DepartmentAPIView)

timesheet_router = routers.DefaultRouter()
timesheet_router.register(r'^api/timesheet', views.TimeSheetViewset)

payslip_router = routers.DefaultRouter()
payslip_router.register(r'^api/payslip', views.PayslipViewset)

timesheet_urls = [
    re_path(r'^timesheet/create/?$', views.CreateTimeSheetView.as_view(), name='timesheet-create'),
    re_path(r'^timesheet/list/?$', views.ListTimeSheetView.as_view(), name='timesheet-list'),
    re_path(r'^timesheet/update/(?P<pk>[\d]+)/?$', views.TimeSheetUpdateView.as_view(), name='timesheet-update'),
    re_path(r'^timesheet/detail/(?P<pk>[\d]+)/?$', views.TimeSheetDetailView.as_view(), name='timesheet-detail'),
    re_path(r'^time-logger/?$', views.TimeLoggerView.as_view(), name='time-logger')

]

pay_officer_urls = [
    re_path(r'^payroll-officer/create/?$', 
        views.PayrollOfficerCreateView.as_view(), 
        name='payroll-officer-create'),
    re_path(r'^payroll-officer/list/?$', 
        views.PayrollOfficerListView.as_view(), name='payroll-officer-list'),
    re_path(r'^payroll-officer/update/(?P<pk>[\d]+)/?$', 
        views.PayrollOfficerUpdateView.as_view(), 
        name='payroll-officer-update'),
    re_path(r'^payroll-officer/detail/(?P<pk>[\d]+)/?$', 
        views.PayrollOfficerDetailView.as_view(), 
        name='payroll-officer-detail'),
    
]

pay_urls = [
    re_path(r'^create-pay-grade/?$', views.PayGradeCreateView.as_view(), 
        name='create-pay-grade'),
    re_path(r'^update-pay-grade/(?P<pk>[\w]+)/?$', 
        views.PayGradeUpdateView.as_view(), name='update-pay-grade'),
    re_path(r'^list-pay-grades/?$', views.PayGradeListView.as_view(), 
        name='list-pay-grades'),
    re_path(r'^list-pay-slips/?$', views.PayslipListView.as_view(), 
        name='list-pay-slips'),
    re_path(r'^pay-slip-detail/(?P<pk>[\w]+)/?$', views.PayslipView.as_view(), 
        name='pay-slip-detail'),
    re_path(r'^pay-slip-pdf/(?P<pk>[\w]+)/?$', views.PayslipPDFView.as_view(), 
        name='pay-slip-pdf'),
    re_path(r'^pay-slip-verify/(?P<pk>[\w]+)/?$', 
        views.PayslipVerificationView.as_view(), name='pay-slip-verify'),
    re_path(r'^pay-slip-delete/(?P<pk>[\w]+)/?$', 
        views.PayslipDeleteView.as_view(), name='pay-slip-delete'),
    re_path(r'^pay-slip-verify-status/(?P<pk>[\w]+)/?$', views.verify_payslip, 
        name='pay-slip-verify-status'),
    re_path(r'^execute-payroll/?$', views.execute_payroll, 
        name='execute-payroll'),
]


employee_urls = [
    re_path(r'^create-employee/?$', views.EmployeeCreateView.as_view(), 
        name='create-employee'),
    re_path(r'^list-employees/?$', views.EmployeeListView.as_view(), 
        name='list-employees'),
    re_path(r'^employee-update/(?P<pk>[\w]+)/?$', 
        views.EmployeeUpdateView.as_view(), name='employee-update'),
    re_path(r'^employee-detail/(?P<pk>[\w]+)/?$', 
        views.EmployeeDetailView.as_view(), name='employee-detail'),
    re_path(r'^employee-delete/(?P<pk>[\w]+)/?$', 
        views.EmployeeDeleteView.as_view(), name='employee-delete'),
    re_path(r'^employee/create-user/(?P<pk>[\w]+)/?$', 
        views.EmployeeUserCreateView.as_view(), name='employee-user-create'),
    re_path(r'^employee/user/reset-password/(?P<pk>[\w]+)/?$', 
        views.EmployeeUserPasswordResetView.as_view(), 
            name='employee-user-password-reset'),
    re_path(r'^employee/delete-user/(?P<pk>[\w]+)/?$', 
        views.remove_employee_user, name='employee-delete-user'),
]

other_urls = [
    re_path(r'^create-allowance/?$', views.AllowanceCreateView.as_view(), 
        name='create-allowance'),
    re_path(r'^update-allowance/(?P<pk>[\w]+)/?$', 
        views.AllowanceUpdateView.as_view(), name='update-allowance'),
    re_path(r'^delete-allowance/(?P<pk>[\w]+)/?$', 
        views.AllowanceDeleteView.as_view(), name='delete-allowance'),
    re_path(r'^create-deduction/?$', views.DeductionCreateView.as_view(), 
        name='create-deduction'),
    re_path(r'^delete-deduction/(?P<pk>[\w]+)/?$', 
        views.DeductionDeleteView.as_view(), name='delete-deduction'),
    re_path(r'^update-deduction/(?P<pk>[\w]+)/?$', 
        views.DeductionUpdateView.as_view(), name='update-deduction'),
    re_path(r'^create-commission/?$', views.CommissionCreateView.as_view(), 
        name='create-commission'),
    re_path(r'^create-payroll-tax/?$', views.PayrollTaxCreateView.as_view(), 
        name='create-payroll-tax'),
    re_path(r'^payroll-tax-list/?$', views.PayrollTaxListView.as_view(), 
        name='payroll-tax-list'),
    re_path(r'^payroll-tax/(?P<pk>[\w]+)/?$', 
        views.PayrollTaxDetailView.as_view(), name='payroll-tax'), 
    re_path(r'^payroll-tax-delete/(?P<pk>[\w]+)/?$', 
        views.PayrollTaxDeleteView.as_view(), name='payroll-tax-delete'), 
    re_path(r'^update-payroll-tax/(?P<pk>[\w]+)/?$', 
        views.PayrollTaxUpdateView.as_view(), name='update-payroll-tax'),  
    re_path(r'^delete-commission/(?P<pk>[\w]+)/?$', 
        views.CommissionDeleteView.as_view(), name='delete-commission'),
    re_path(r'^update-commission/(?P<pk>[\w]+)/?$', 
        views.CommissionUpdateView.as_view(), name='update-commission'),
    re_path(r'^util-list/?$', views.UtilsListView.as_view(), name='util-list'),
    re_path(r'^config/(?P<pk>[\d]+)/?$', views.PayrollConfig.as_view(), 
        name='config'),
    re_path(r'^manual-config/?$', views.ManualPayrollConfig.as_view(), name='manual-config'),
    re_path(r'^payroll-date/create/?$', views.CreatePayrollDateView.as_view(), name='payroll-date-create'),
    re_path(r'^payroll-date/update/(?P<pk>[\d]+)/?$', views.PayrollDateUpdateView.as_view(), name='payroll-date-update'),
    re_path(r'^payroll-date/detail/(?P<pk>[\d]+)/?$', views.PayrollDateDetailView.as_view(), name='payroll-date-detail'),
    re_path(r'^payroll-date/delete/(?P<pk>[\d]+)/?$', views.PayrollDateDeleteView.as_view(), name='payroll-date-delete'),
    re_path(r'^payroll-date/list/?$', views.PayrollDateListView.as_view(), name='payroll-date-list'),
    
]

leave_urls = [
    re_path(r'^leave-request/?$', views.LeaveDayRequestView.as_view(),
        name='leave-request'),
    re_path(r'^leave-calendar/*', views.LeaveCalendarView.as_view(),
        name='leave-calendar'),
    re_path(r'^leave-list/?$', views.LeaveRequestList.as_view() ,
        name='leave-list' ),
    re_path(r'^leave-detail/(?P<pk>[\d]+)/?$', 
        views.LeaveDayDetailView.as_view() ,
        name='leave-detail'),
    re_path(r'^leave-authorization/(?P<pk>[\d]+)/?$', 
        views.LeaveAuthorizationView.as_view(),
        name='leave-authorization'),
    re_path(r'^api/month/(?P<year>[\d]{4})/(?P<month>[\d]{2})', 
        views.get_month_data),
    re_path(r'^api/year/(?P<year>[\d]{4})/?$', 
        views.get_year_data)
    
]

department_urls = [
    path('department/list', views.DepartmentListView.as_view(), name="department-list"),
    path('department/create', views.DepartmentCreateView.as_view(), name="department-create"),
    path('department/detail/<int:pk>', views.DepartmentDetailView.as_view(), name="department-detail"),
    path('department/update/<int:pk>', views.DepartmentUpdateView.as_view(), name="department-update")

]

urlpatterns = [
    re_path(r'^$', views.DashBoard.as_view(), name='dashboard')
] + other_urls + employee_urls + pay_urls + \
    employee_router.urls + payslip_router.urls + \
    timesheet_urls + timesheet_router.urls + pay_officer_urls + \
    leave_urls + department_urls + department_router.urls

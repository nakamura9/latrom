from django.urls import re_path
from . import views
from rest_framework import routers

employee_router = routers.DefaultRouter()
employee_router.register(r'^api/employee', views.EmployeeViewSet)

payslip_router = routers.DefaultRouter()
payslip_router.register(r'^api/payslip', views.PayslipViewset)


pay_urls = [
    re_path(r'^create-pay-grade/?$', views.PayGradeCreateView.as_view(), name='create-pay-grade'),
    re_path(r'^update-pay-grade/(?P<pk>[\w]+)/?$', views.PayGradeUpdateView.as_view(), name='update-pay-grade'),
    re_path(r'^list-pay-grades/?$', views.PayGradeListView.as_view(), name='list-pay-grades'),
    re_path(r'^list-pay-slips/?$', views.PayslipListView.as_view(), name='list-pay-slips'),
    re_path(r'^pay-slip-detail/(?P<pk>[\w]+)/?$', views.PayslipView.as_view(), name='pay-slip-detail'),
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
]

other_urls = [
    re_path(r'^create-allowance/?$', views.AllowanceCreateView.as_view(), name='create-allowance'),
    re_path(r'^update-allowance/(?P<pk>[\w]+)/?$', views.AllowanceUpdateView.as_view(), name='update-allowance'),
    re_path(r'^delete-allowance/(?P<pk>[\w]+)/?$', views.AllowanceDeleteView.as_view(), name='delete-allowance'),
    re_path(r'^create-deduction/?$', views.DeductionCreateView.as_view(), name='create-deduction'),
    re_path(r'^delete-deduction/(?P<pk>[\w]+)/?$', views.DeductionDeleteView.as_view(), name='delete-deduction'),
    re_path(r'^update-deduction/(?P<pk>[\w]+)/?$', views.DeductionUpdateView.as_view(), name='update-deduction'),
    re_path(r'^create-commission/?$', views.CommissionCreateView.as_view(), name='create-commission'),
    re_path(r'^create-payroll-tax/?$', views.PayrollTaxCreateView.as_view(), name='create-payroll-tax'),
    re_path(r'^payroll-tax/(?P<pk>[\w]+)/?$', views.PayrollTaxDetailView.as_view(), name='payroll-tax'), 
    re_path(r'^payroll-tax-delete/(?P<pk>[\w]+)/?$', views.PayrollTaxDeleteView.as_view(), name='payroll-tax-delete'), 
    re_path(r'^update-payroll-tax/(?P<pk>[\w]+)/?$', views.PayrollTaxUpdateView.as_view(), name='update-payroll-tax'),  
    re_path(r'^delete-commission/(?P<pk>[\w]+)/?$', views.CommissionDeleteView.as_view(), name='delete-commission'),
    re_path(r'^update-commission/(?P<pk>[\w]+)/?$', views.CommissionUpdateView.as_view(), name='update-commission'),
    re_path(r'^util-list/?$', views.UtilsListView.as_view(), name='util-list'),
    re_path(r'^config/(?P<pk>[\d]+)/?$', views.PayrollConfig.as_view(), name='config'),
    re_path(r'^manual-config/?$', views.ManualPayrollConfig.as_view(), name='manual-config'),
    
]

urlpatterns = [
    re_path(r'^$', views.DashBoard.as_view(), name='dashboard')
] + other_urls + employee_urls + pay_urls + \
    employee_router.urls + payslip_router.urls
from django.urls import re_path, path
from rest_framework import routers

from employees import views

payslip_router = routers.DefaultRouter()
payslip_router.register(r'^api/payslip', views.PayslipViewset)



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
    re_path(r'^pay-grade-detail/(?P<pk>[\w]+)/?$', 
        views.PayGradeDetailView.as_view(), name='pay-grade-detail'),
    re_path(r'^list-pay-grades/?$', views.PayGradeListView.as_view(), 
        name='list-pay-grades'),
    re_path(r'^list-pay-slips/?$', views.PayslipListView.as_view(), 
        name='list-pay-slips'),
    re_path(r'^list-employee-pay-slips/(?P<pk>[\w]+)/?$', 
        views.EmployeePayslipListView.as_view(), 
        name='list-pay-slips-employee'),
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
] + pay_officer_urls + payslip_router.urls

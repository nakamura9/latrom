from django.conf.urls import url
import views
from rest_framework import routers

employee_router = routers.DefaultRouter()
employee_router.register(r'^api/employee', views.EmployeeViewSet)

payslip_router = routers.DefaultRouter()
payslip_router.register(r'^api/payslip', views.PayslipViewset)


pay_urls = [
    url(r'^create-pay-grade/?$', views.PayGradeCreateView.as_view(), name='create-pay-grade'),
    url(r'^update-pay-grade/(?P<pk>[\w]+)/?$', views.PayGradeUpdateView.as_view(), name='update-pay-grade'),
    url(r'^list-pay-grades/?$', views.PayGradeListView.as_view(), name='list-pay-grades'),
    url(r'^list-pay-slips/?$', views.PayslipListView.as_view(), name='list-pay-slips'),
    url(r'^pay-slip-detail/(?P<pk>[\w]+)/?$', views.PayslipView.as_view(), name='pay-slip-detail'),
]


employee_urls = [
    url(r'^create-employee/?$', views.EmployeeCreateView.as_view(), 
        name='create-employee'),
    url(r'^list-employees/?$', views.EmployeeListView.as_view(), 
        name='list-employees'),
    url(r'^employee-update/(?P<pk>[\w]+)/?$', 
        views.EmployeeUpdateView.as_view(), name='employee-update'),
    url(r'^employee-detail/(?P<pk>[\w]+)/?$', 
        views.EmployeeDetailView.as_view(), name='employee-detail'),
    url(r'^employee-delete/(?P<pk>[\w]+)/?$', 
        views.EmployeeDeleteView.as_view(), name='employee-delete'),
]

other_urls = [
    url(r'^create-allowance/?$', views.AllowanceCreateView.as_view(), name='create-allowance'),
    url(r'^update-allowance/(?P<pk>[\w]+)/?$', views.AllowanceUpdateView.as_view(), name='update-allowance'),
    url(r'^delete-allowance/(?P<pk>[\w]+)/?$', views.AllowanceDeleteView.as_view(), name='delete-allowance'),
    url(r'^create-deduction/?$', views.DeductionCreateView.as_view(), name='create-deduction'),
    url(r'^delete-deduction/(?P<pk>[\w]+)/?$', views.DeductionDeleteView.as_view(), name='delete-deduction'),
    url(r'^update-deduction/(?P<pk>[\w]+)/?$', views.DeductionUpdateView.as_view(), name='update-deduction'),
    url(r'^create-commission/?$', views.CommissionCreateView.as_view(), name='create-commission'),
    url(r'^create-payroll-tax/?$', views.PayrollTaxCreateView.as_view(), name='create-payroll-tax'),
    url(r'^payroll-tax/(?P<pk>[\w]+)/?$', views.PayrollTaxDetailView.as_view(), name='payroll-tax'), 
    url(r'^payroll-tax-delete/(?P<pk>[\w]+)/?$', views.PayrollTaxDeleteView.as_view(), name='payroll-tax-delete'), 
    url(r'^update-payroll-tax/(?P<pk>[\w]+)/?$', views.PayrollTaxUpdateView.as_view(), name='update-payroll-tax'),  
    url(r'^delete-commission/(?P<pk>[\w]+)/?$', views.CommissionDeleteView.as_view(), name='delete-commission'),
    url(r'^update-commission/(?P<pk>[\w]+)/?$', views.CommissionUpdateView.as_view(), name='update-commission'),
    url(r'^util-list/?$', views.UtilsListView.as_view(), name='util-list'),
    
]

urlpatterns = [
    url(r'^$', views.DashBoard.as_view(), name='dashboard')
] + other_urls + employee_urls + pay_urls + \
    employee_router.urls + payslip_router.urls
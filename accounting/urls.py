from django.conf.urls import url
import views
from rest_framework import routers

tax_router = routers.DefaultRouter()
tax_router.register(r'^api/tax', views.TaxViewset)

employee_router = routers.DefaultRouter()
employee_router.register(r'^api/employee', views.EmployeeViewSet)

payslip_router = routers.DefaultRouter()
payslip_router.register(r'^api/payslip', views.PayslipViewset)
'''
direct_urls = [
    url(r'^create-direct-purchase/?$', views.DirectPurchaseCreateView.as_view(), name='create-direct-purchase'),
    url(r'^list-direct-purchases/?$', views.DirectPurchaseListView.as_view(), name='list-direct-purchases'),
    url(r'^transaction-update/(?P<pk>[\w]+)/?$', 
        views.TransactionUpdateView.as_view(), name='transaction-update'),
    url(r'^transaction-delete/(?P<pk>[\w]+)/?$', 
        views.TransactionDeleteView.as_view(), name='transaction-delete'),
    ]
'''
urlpatterns =[
    url(r'^$', views.Dashboard.as_view(), name='dashboard'),
    url(r'^create-transaction/?$', views.TransactionCreateView.as_view(), 
        name='create-transaction'),
    url(r'^create-employee/?$', views.EmployeeCreateView.as_view(), 
        name='create-employee'),
    url(r'^list-employees/?$', views.EmployeeListView.as_view(), 
        name='list-employees'),
    url(r'^employee-update/(?P<pk>[\w]+)/?$', 
        views.EmployeeUpdateView.as_view(), name='employee-update'),
    url(r'^employee-detail/(?P<pk>[\w]+)/?$', 
        views.EmployeeDetailView.as_view(), name='employee-detail'),
    url(r'^transaction-detail/(?P<pk>[\w]+)/?$', views.TransactionDetailView.as_view(), 
        name='transaction-detail'),
    url(r'^create-account/?$', views.AccountCreateView.as_view(), 
        name='create-account'),
    url(r'^account-detail/(?P<pk>[\w]+)/?$', views.AccountDetailView.as_view(), 
        name='account-detail'),
    url(r'^account-update/(?P<pk>[\w]+)/?$', views.AccountUpdateView.as_view(), 
        name='account-update'),
    url(r'^account-list/?$', views.AccountListView.as_view(), 
        name='account-list'),
    url(r'^create-journal/?$', views.JournalCreateView.as_view(), 
        name='create-journal'),
    url(r'^journal-list/?$', views.JournalListView.as_view(), 
        name='journal-list'),
    url(r'^journal-detail/(?P<pk>[\w]+)/?$', views.JournalDetailView.as_view(), 
        name='journal-detail'),
    url(r'^transfer/?$', views.AccountTransferPage.as_view(), 
        name='transfer'),
    url(r'^non-invoiced-cash-sale/?$', views.NonInvoicedCashSale.as_view() ,name='non-invoiced-cash-sale'),
    url(r'^create-allowance/?$', views.AllowanceCreateView.as_view(), name='create-allowance'),
    url(r'^create-deduction/?$', views.DeductionCreateView.as_view(), name='create-deduction'),
    url(r'^create-commission/?$', views.CommissionCreateView.as_view(), name='create-commission'),
    url(r'^create-pay-grade/?$', views.PayGradeCreateView.as_view(), name='create-pay-grade'),
    url(r'^update-pay-grade/(?P<pk>[\w]+)/?$', views.PayGradeUpdateView.as_view(), name='update-pay-grade'),
    url(r'^list-pay-grades/?$', views.PayGradeListView.as_view(), name='list-pay-grades'),
    url(r'^payroll-config/?$', views.PayrollConfigView.as_view(), name='payroll-config'),
    url(r'^list-pay-slips/?$', views.PayslipListView.as_view(), name='list-pay-slips'),
    url(r'^pay-slip-detail/(?P<pk>[\w]+)/?$', views.PayslipView.as_view(), name='pay-slip-detail'),
    
] + tax_router.urls + employee_router.urls + payslip_router.urls

#url(r'^payslip/?$', views.PayView.as_view(), name='payslip')
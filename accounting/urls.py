from django.conf.urls import url
import views
from rest_framework import routers

tax_router = routers.DefaultRouter()
tax_router.register(r'^api/tax', views.TaxViewset)

employee_router = routers.DefaultRouter()
employee_router.register(r'^api/employee', views.EmployeeViewSet)

account_router = routers.DefaultRouter()
account_router.register(r'^api/account', views.AccountViewSet)


payslip_router = routers.DefaultRouter()
payslip_router.register(r'^api/payslip', views.PayslipViewset)

pay_urls = [
    url(r'^create-pay-grade/?$', views.PayGradeCreateView.as_view(), name='create-pay-grade'),
    url(r'^update-pay-grade/(?P<pk>[\w]+)/?$', views.PayGradeUpdateView.as_view(), name='update-pay-grade'),
    url(r'^list-pay-grades/?$', views.PayGradeListView.as_view(), name='list-pay-grades'),
    url(r'^payroll-config/?$', views.PayrollConfigView.as_view(), name='payroll-config'),
    url(r'^list-pay-slips/?$', views.PayslipListView.as_view(), name='list-pay-slips'),
    url(r'^pay-slip-detail/(?P<pk>[\w]+)/?$', views.PayslipView.as_view(), name='pay-slip-detail'),
]
entry_urls = [
    url(r'^create-entry/?$', views.JournalEntryCreateView.as_view(), 
    name='create-entry'),
    url(r'^compound-entry/?$', views.ComplexEntryView.as_view(), 
    name='compound-entry'),
    url(r'^entry-detail/(?P<pk>[\w]+)/?$', views.JournalEntryDetailView.as_view(), 
    name='entry-detail'),
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
account_urls = [
    url(r'^create-account/?$', views.AccountCreateView.as_view(), 
        name='create-account'),
    
    url(r'^account-detail/(?P<pk>[\w]+)/?$', views.AccountDetailView.as_view(), 
        name='account-detail'),
    url(r'^account-update/(?P<pk>[\w]+)/?$', views.AccountUpdateView.as_view(), 
        name='account-update'),
    url(r'^account-list/?$', views.AccountListView.as_view(), 
        name='account-list'),]

misc_urls = [    
    url(r'^transfer/?$', views.AccountTransferPage.as_view(), 
    name='transfer'),
    url(r'^non-invoiced-cash-sale/?$', views.NonInvoicedCashSale.as_view() ,name='non-invoiced-cash-sale'),
    url(r'^create-allowance/?$', views.AllowanceCreateView.as_view(), name='create-allowance'),
    url(r'^update-allowance/(?P<pk>[\w]+)/?$', views.AllowanceUpdateView.as_view(), name='update-allowance'),
    url(r'^delete-allowance/(?P<pk>[\w]+)/?$', views.AllowanceDeleteView.as_view(), name='delete-allowance'),
    url(r'^create-deduction/?$', views.DeductionCreateView.as_view(), name='create-deduction'),
    url(r'^delete-deduction/(?P<pk>[\w]+)/?$', views.DeductionDeleteView.as_view(), name='delete-deduction'),
    url(r'^update-deduction/(?P<pk>[\w]+)/?$', views.DeductionUpdateView.as_view(), name='update-deduction'),
    url(r'^create-commission/?$', views.CommissionCreateView.as_view(), name='create-commission'),
    url(r'^delete-commission/(?P<pk>[\w]+)/?$', views.CommissionDeleteView.as_view(), name='delete-commission'),
    url(r'^update-commission/(?P<pk>[\w]+)/?$', views.CommissionUpdateView.as_view(), name='update-commission'),
    url(r'^create-tax/?$', views.TaxCreateView.as_view(), name='create-tax'),
    url(r'^delete-tax/(?P<pk>[\w]+)/?$', views.TaxDeleteView.as_view(), name='delete-tax'),
    url(r'^update-tax/(?P<pk>[\w]+)/?$', views.TaxUpdateView.as_view(), name='update-tax'),
    url(r'^util-list/?$', views.UtilsListView.as_view(), name='util-list'),
    url(r'^config/?$', views.AccountConfigView.as_view(), name='config'),
    url(r'^direct-payment/?$', views.DirectPaymentFormView.as_view(), name='direct-payment'),
    url(r'^direct-payment-list/?$', views.DirectPaymentList.as_view(), name='direct-payment-list')]


journal_urls = [
    url(r'^create-journal/?$', views.JournalCreateView.as_view(), 
        name='create-journal'),
    url(r'^journal-list/?$', views.JournalListView.as_view(), 
        name='journal-list'),
    url(r'^journal-detail/(?P<pk>[\w]+)/?$', views.JournalDetailView.as_view(), 
        name='journal-detail')
    ]


urlpatterns =[
    url(r'^$', views.Dashboard.as_view(), name='dashboard'),
] + tax_router.urls + employee_router.urls + payslip_router.urls + \
    misc_urls + account_urls + employee_urls + journal_urls + \
    entry_urls + pay_urls + account_router.urls

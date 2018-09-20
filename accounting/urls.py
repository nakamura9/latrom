from django.urls import re_path
from rest_framework import routers

from . import report_views, views

tax_router = routers.DefaultRouter()
tax_router.register(r'^api/tax', views.TaxViewset)

account_router = routers.DefaultRouter()
account_router.register(r'^api/account', views.AccountViewSet)

assets = views.AssetViewGroup()
expenses = views.ExpenseViewGroup()

expense_router = routers.DefaultRouter()
expense_router.register(r'^api/expense', views.ExpenseAPIView)

report_urls = [
    re_path(r'^balance-sheet/?$', report_views.BalanceSheet.as_view(), name='balance-sheet'),
    re_path(r'^income-statement/?$', report_views.IncomeStatement.as_view(), name='income-statement'),
    re_path(r'^income-statement-form/?$', report_views.IncomeStatementFormView.as_view(), name='income-statement-form')
]

entry_urls = [
    re_path(r'^create-entry/?$', views.JournalEntryCreateView.as_view(), 
    name='create-entry'),
    re_path(r'^compound-entry/?$', views.ComplexEntryView.as_view(), 
    name='compound-entry'),
    re_path(r'^entry-detail/(?P<pk>[\w]+)/?$', views.JournalEntryDetailView.as_view(), 
    name='entry-detail'),
]
account_urls = [
    re_path(r'^create-account/?$', views.AccountCreateView.as_view(), 
        name='create-account'),
    
    re_path(r'^account-detail/(?P<pk>[\w]+)/?$', views.AccountDetailView.as_view(), 
        name='account-detail'),
    re_path(r'^account-update/(?P<pk>[\w]+)/?$', views.AccountUpdateView.as_view(), 
        name='account-update'),
    re_path(r'^account-list/?$', views.AccountListView.as_view(), 
        name='account-list'),]

misc_urls = [    
    re_path(r'^transfer/?$', views.AccountTransferPage.as_view(), 
    name='transfer'),
    re_path(r'^non-invoiced-cash-sale/?$', views.NonInvoicedCashSale.as_view() ,name='non-invoiced-cash-sale'),
    re_path(r'^create-tax/?$', views.TaxCreateView.as_view(), name='create-tax'),
    re_path(r'^tax-list/?$', views.TaxListView.as_view(), name='tax-list'),
    re_path(r'^delete-tax/(?P<pk>[\w]+)/?$', views.TaxDeleteView.as_view(), name='delete-tax'),
    re_path(r'^update-tax/(?P<pk>[\w]+)/?$', views.TaxUpdateView.as_view(), name='update-tax'),
    re_path(r'^config/(?P<pk>[\d]+)/?$', views.AccountConfigView.as_view(), name='config'),
    re_path(r'^direct-payment/?$', views.DirectPaymentFormView.as_view(), name='direct-payment'),
    re_path(r'^direct-payment-list/?$', views.DirectPaymentList.as_view(), name='direct-payment-list'),
    re_path(r'^create-bookkeeper/?$', views.BookkeeperCreateView.as_view(), name = 'create-bookkeeper'),
    re_path(r'^bookkeeper-list/?$', views.BookkeeperListView.as_view(), name='bookkeeper-list')]


journal_urls = [
    re_path(r'^create-journal/?$', views.JournalCreateView.as_view(), 
        name='create-journal'),
    re_path(r'^journal-list/?$', views.JournalListView.as_view(), 
        name='journal-list'),
    re_path(r'^journal-detail/(?P<pk>[\w]+)/?$', views.JournalDetailView.as_view(), 
        name='journal-detail')
    ]


urlpatterns =[
    re_path(r'^$', views.Dashboard.as_view(), name='dashboard'),
] + tax_router.urls +  misc_urls + account_urls  + journal_urls + \
    entry_urls  + account_router.urls + assets.urls + expenses.urls + \
    report_urls + expense_router.urls

from django.conf.urls import url
import views
from rest_framework import routers

tax_router = routers.DefaultRouter()
tax_router.register(r'^api/tax', views.TaxViewset)

account_router = routers.DefaultRouter()
account_router.register(r'^api/account', views.AccountViewSet)

assets = views.AssetViewGroup()
expenses = views.ExpenseViewGroup()

entry_urls = [
    url(r'^create-entry/?$', views.JournalEntryCreateView.as_view(), 
    name='create-entry'),
    url(r'^compound-entry/?$', views.ComplexEntryView.as_view(), 
    name='compound-entry'),
    url(r'^entry-detail/(?P<pk>[\w]+)/?$', views.JournalEntryDetailView.as_view(), 
    name='entry-detail'),
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
    url(r'^create-tax/?$', views.TaxCreateView.as_view(), name='create-tax'),
    url(r'^delete-tax/(?P<pk>[\w]+)/?$', views.TaxDeleteView.as_view(), name='delete-tax'),
    url(r'^update-tax/(?P<pk>[\w]+)/?$', views.TaxUpdateView.as_view(), name='update-tax'),
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
] + tax_router.urls +  misc_urls + account_urls  + journal_urls + \
    entry_urls  + account_router.urls + assets.urls + expenses.urls

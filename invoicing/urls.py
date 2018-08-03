from django.conf.urls import url
import views
import report_views
from rest_framework.routers import DefaultRouter


customer_router = DefaultRouter()
customer_router.register(r'api/customer', views.CustomerAPIViewSet, base_name='customer')

sales_rep_router = DefaultRouter()
sales_rep_router.register(r'api/sales-rep', views.SalesRepsAPIViewSet, base_name='sales-rep')



report_urls = [
    url(r'^customer-statement-form/?$', 
        report_views.CustomerReportFormView.as_view(),
             name='customer-statement-form'),
    url(r'^customer-statement/?$', report_views.CustomerStatement.as_view(),
             name='customer-statement'),
    url(r'^invoice-aging/?$', report_views.InvoiceAgingReport.as_view(),
             name='invoice-aging'),
]

sales_router = DefaultRouter()
sales_router.register('api/sales-invoice', views.SalesInvoiceAPIViewSet)

sales_urls = [
    url(r'^create-sales-invoice/?$', views.SalesInvoiceCreateView.as_view(), name='create-sales-invoice'),
    url(r'^sales-invoice-detail/(?P<pk>[\d]+)/?$', views.SalesInvoiceDetailView.as_view(), name='sales-invoice-detail'),
    url(r'^sales-invoice-update/(?P<pk>[\d]+)/?$', views.SalesInvoiceUpdateView.as_view(), name='sales-invoice-update'),
    url(r'^sales-invoice-payment/(?P<pk>[\d]+)/?$', views.SalesInvoicePaymentView.as_view(), name='sales-invoice-payment'),
    url(r'^sales-invoice-payment-detail/(?P<pk>[\d]+)/?$', views.SalesInvoicePaymentDetailView.as_view(), name='sales-invoice-payment-detail'),
    url(r'^sales-draft-update/(?P<pk>[\d]+)/?$', views.SalesDraftUpdateView.as_view(), name='sales-draft-update'),
    url(r'^sales-invoice-list/?$', views.SalesInvoiceListView.as_view(), name='sales-invoice-list'),
] + sales_router.urls

service_urls = [
    url(r'^create-service-invoice/?$', views.ServiceInvoiceCreateView.as_view(), name='create-service-invoice'),
    url(r'^service-invoice-detail/(?P<pk>[\d]+)/?$', views.ServiceInvoiceDetailView.as_view(), name='service-invoice-detail'),
    url(r'^service-invoice-list/?$', views.ServiceInvoiceListView.as_view(), name='service-invoice-list'),
]

bill_urls = [
    url(r'^create-bill/?$', views.BillCreateView.as_view(), name='create-bill'),
    url(r'^bill-detail/(?P<pk>[\d]+)/?$', views.BillDetailView.as_view(), name='bill-detail'),
    url(r'^bill-list/?$', views.BillListView.as_view(), name='bill-list'),
]

combined_invoice_urls = [
    url(r'^create-combined-invoice/?$', views.CombinedInvoiceCreateView.as_view(), name='create-combined-invoice'),
    url(r'^combined-invoice-detail/(?P<pk>[\d]+)/?$', views.CombinedInvoiceDetailView.as_view(), name='combined-invoice-detail'),
    url(r'^combined-invoice-list/?$', views.CombinedInvoiceListView.as_view(), name='combined-invoice-list'),
]

urlpatterns = [
    url(r'^$', views.Home.as_view(), name="home"),
    url(r'^config/(?P<pk>[\d]+)/?$', views.ConfigView.as_view(), name="config"),
    url(r'^create-customer$', views.CustomerCreateView.as_view(), name='create-customer'),
    url(r'^quick-customer$', views.QuickCustomerCreateView.as_view(), name='quick-customer'),
    url(r'^update-customer/(?P<pk>[\w]+)$', views.CustomerUpdateView.as_view(), name='update-customer'),
    url(r'^delete-customer/(?P<pk>[\w]+)$', views.CustomerDeleteView.as_view(), name='delete-customer'),
    url(r'^customer-list$', views.CustomerListView.as_view(), name='customers-list'),
    url(r'^create-sales-rep$', views.SalesRepCreateView.as_view(), name='create-sales-rep'),
    url(r'^update-sales-rep/(?P<pk>[\w]+)$', views.SalesRepUpdateView.as_view(), name='update-sales-rep'),
    url(r'^delete-sales-rep/(?P<pk>[\w]+)$', views.SalesRepDeleteView.as_view(), name='delete-sales-rep'),
    url(r'^sales-reps-list$', views.SalesRepListView.as_view(), name='sales-reps-list'),
    url(r'^credit-note-create/(?P<pk>[\w]+)/?$', views.CreditNoteCreateView.as_view(), name='credit-note-create'),
    url(r'^credit-note-list/?$', views.CreditNoteListView.as_view(), name='credit-note-list'),
    url(r'^credit-note-detail/(?P<pk>[\w]+)/?$', views.CreditNoteDetailView.as_view(), name='credit-note-detail'),
    url(r'^api/config/(?P<pk>[\d]+)/?$', views.ConfigAPIView.as_view(), name='api-config')
    
    
] +  customer_router.urls + sales_rep_router.urls + \
    report_urls + sales_urls + bill_urls + service_urls + \
    combined_invoice_urls
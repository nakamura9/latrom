from django.conf.urls import url
import views
import report_views
from rest_framework.routers import DefaultRouter


customer_router = DefaultRouter()
customer_router.register(r'api/customer', views.CustomerAPIViewSet, base_name='customer')

invoice_router = DefaultRouter()
invoice_router.register(r'api/invoice', views.InvoiceAPIViewSet, base_name='invoice')

payment_router = DefaultRouter()
payment_router.register(r'api/payment', views.PaymentAPIViewSet, base_name='payment')

sales_rep_router = DefaultRouter()
sales_rep_router.register(r'api/sales-rep', views.SalesRepsAPIViewSet, base_name='sales-rep')


invoice_item_router = DefaultRouter()
invoice_item_router.register(r'api/invoice-item', views.InvoiceItemAPIViewSet, base_name='invoice-item')


quote_router = DefaultRouter()
quote_router.register(r'api/quote', views.QuoteAPIViewSet, base_name='quote-api')


quote_item_router = DefaultRouter()
quote_item_router.register(r'api/quote', views.QuoteItemAPIViewSet, base_name='quote-api')


urlpatterns = [
    url(r'^$', views.Home.as_view(), name="home"),
    url(r'^config/?$', views.ConfigView.as_view(), name="config"),
    url(r'^create-customer$', views.CustomerCreateView.as_view(), name='create-customer'),
    url(r'^quick-customer$', views.QuickCustomerCreateView.as_view(), name='quick-customer'),
    url(r'^update-customer/(?P<pk>[\w]+)$', views.CustomerUpdateView.as_view(), name='update-customer'),
    url(r'^delete-customer/(?P<pk>[\w]+)$', views.CustomerDeleteView.as_view(), name='delete-customer'),
    url(r'^payments-list$', views.PaymentListView.as_view(), name='payments-list'),
    url(r'^create-payment$', views.PaymentCreateView.as_view(), name='create-payment'),
    url(r'^update-payment/(?P<pk>[\w]+)$', views.PaymentUpdateView.as_view(), name='update-payment'),
    url(r'^delete-payment/(?P<pk>[\w]+)$', views.PaymentDeleteView.as_view(), name='delete-payment'),
    url(r'^customer-list$', views.CustomerListView.as_view(), name='customers-list'),
    url(r'^create-sales-rep$', views.SalesRepCreateView.as_view(), name='create-sales-rep'),
    url(r'^update-sales-rep/(?P<pk>[\w]+)$', views.SalesRepUpdateView.as_view(), name='update-sales-rep'),
    url(r'^delete-sales-rep/(?P<pk>[\w]+)$', views.SalesRepDeleteView.as_view(), name='delete-sales-rep'),
    url(r'^sales-reps-list$', views.SalesRepListView.as_view(), name='sales-reps-list'),
    url(r'^invoices-list$', views.InvoiceListView.as_view(), name='invoices-list'),
    url(r'^create-invoice$', views.InvoiceCreateView.as_view(), name='create-invoice'),
    url(r'^update-invoice/(?P<pk>[\w]+)$', views.InvoiceUpdateView.as_view(), name='update-invoice'),
    url(r'^invoice-details/(?P<pk>[\w]+)$', views.InvoiceDetailView.as_view(), name='invoice-details'),
    url(r'^delete-invoice/(?P<pk>[\w]+)$', views.InvoiceDeleteView.as_view(), name='delete-invoice'),
    url(r'^delete-quote/(?P<pk>[\w]+)$', views.QuoteDeleteView.as_view(), name='delete-quote'),
    url(r'^quote-detail/(?P<pk>[\w]+)$', views.QuoteDetailView.as_view(), name='quote-detail'),
    url(r'^quote-update/(?P<pk>[\w]+)$', views.QuoteUpdateView.as_view(), name='quote-update'),
    url(r'^create-quote$', views.QuoteCreateView.as_view(), name='create-quote'),
    url(r'^quote-list$', views.QuoteListView.as_view(), name='quote-list'),
    
    url(r'^receipt/(?P<pk>[\w]+)$', views.ReceiptDetailView.as_view(), name='receipt'),
    url(r'^payment-from-invoice/(?P<pk>[\w]+)$', views.create_payment_from_invoice, name='payment-from-invoice'),
    url(r'^invoice-from-quote/(?P<pk>[\w]+)$', views.create_invoice_from_quote, name='invoice-from-quote'),
    url(r'^credit-note-create/?$', views.CreditNoteCreateView.as_view(), name='credit-note-create'),
    url(r'^credit-note-list/?$', views.CreditNoteListView.as_view(), name='credit-note-list'),
    url(r'^customer-statement-form/?$', report_views.CustomerStatementReportFormView.as_view(), 
        name='customer-statement-form'),
    url(r'^customer-statement/?$', 
        report_views.CustomerStatementReport.as_view(), name='customer-statement'),
    url(r'^credit-note-detail/(?P<pk>[\w]+)/?$', views.CreditNoteDetailView.as_view(), name='credit-note-detail'),
    
] +  customer_router.urls + invoice_router.urls + \
    payment_router.urls + sales_rep_router.urls +  invoice_item_router.urls + \
    quote_router.urls + quote_item_router.urls
from django.conf.urls import url
from invoicing import views
from rest_framework.routers import DefaultRouter

sales_router = DefaultRouter()
sales_router.register('api/sales-invoice', views.SalesInvoiceAPIViewSet)

credit_note_urls = [
    url(r'^credit-note-create/(?P<pk>[\w]+)/?$', views.CreditNoteCreateView.as_view(), name='credit-note-create'),
    url(r'^credit-note-list/?$', views.CreditNoteListView.as_view(), name='credit-note-list'),
    url(r'^credit-note-detail/(?P<pk>[\w]+)/?$', views.CreditNoteDetailView.as_view(), name='credit-note-detail'),
]

sales_urls = [
    url(r'^create-sales-invoice/?$', views.SalesInvoiceCreateView.as_view(), name='create-sales-invoice'),
    url(r'^sales-invoice-detail/(?P<pk>[\d]+)/?$', views.SalesInvoiceDetailView.as_view(), name='sales-invoice-detail'),
    url(r'^sales-invoice-pdf/(?P<pk>[\d]+)/?$', views.SalesInvoicePDFView.as_view(), name='sales-invoice-pdf'),
    url(r'^sales-invoice-update/(?P<pk>[\d]+)/?$', 
        views.SalesInvoiceUpdateView.as_view(), name='sales-invoice-update'),
    url(r'^sales-invoice-payment/(?P<pk>[\d]+)/?$', 
        views.SalesInvoicePaymentView.as_view(), name='sales-invoice-payment'),
    url(r'^sales-invoice-payment-detail/(?P<pk>[\d]+)/?$', 
        views.SalesInvoicePaymentDetailView.as_view(), 
        name='sales-invoice-payment-detail'),
    url(r'^sales-draft-update/(?P<pk>[\d]+)/?$', 
        views.SalesDraftUpdateView.as_view(), name='sales-draft-update'),
    url(r'^sales-invoice-returns/(?P<pk>[\d]+)/?$', 
        views.SalesInvoiceReturnsDetailView.as_view(), 
        name='sales-invoice-returns'),
    url(r'^sales-invoice-email/(?P<pk>[\d]+)/?$', 
        views.SalesInvoiceEmailSendView.as_view(), 
        name='sales-invoice-email'),
    url(r'^sales-invoice-list/?$', views.SalesInvoiceListView.as_view(), name='sales-invoice-list'),
] + sales_router.urls + credit_note_urls

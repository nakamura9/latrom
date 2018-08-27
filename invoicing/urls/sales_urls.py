from django.urls import re_path
from invoicing import views
from rest_framework.routers import DefaultRouter

sales_router = DefaultRouter()
sales_router.register('api/sales-invoice', views.SalesInvoiceAPIViewSet)

credit_note_urls = [
    re_path(r'^credit-note-create/(?P<pk>[\w]+)/?$', views.CreditNoteCreateView.as_view(), name='credit-note-create'),
    re_path(r'^credit-note-list/?$', views.CreditNoteListView.as_view(), name='credit-note-list'),
    re_path(r'^credit-note-detail/(?P<pk>[\w]+)/?$', views.CreditNoteDetailView.as_view(), name='credit-note-detail'),
]

sales_urls = [
    re_path(r'^create-sales-invoice/?$', views.SalesInvoiceCreateView.as_view(), name='create-sales-invoice'),
    re_path(r'^sales-invoice-detail/(?P<pk>[\d]+)/?$', views.SalesInvoiceDetailView.as_view(), name='sales-invoice-detail'),
    re_path(r'^sales-invoice-pdf/(?P<pk>[\d]+)/?$', views.SalesInvoicePDFView.as_view(), name='sales-invoice-pdf'),
    re_path(r'^sales-invoice-update/(?P<pk>[\d]+)/?$', 
        views.SalesInvoiceUpdateView.as_view(), name='sales-invoice-update'),
    re_path(r'^sales-invoice-payment/(?P<pk>[\d]+)/?$', 
        views.SalesInvoicePaymentView.as_view(), name='sales-invoice-payment'),
    re_path(r'^sales-invoice-payment-detail/(?P<pk>[\d]+)/?$', 
        views.SalesInvoicePaymentDetailView.as_view(), 
        name='sales-invoice-payment-detail'),
    re_path(r'^sales-draft-update/(?P<pk>[\d]+)/?$', 
        views.SalesDraftUpdateView.as_view(), name='sales-draft-update'),
    re_path(r'^sales-invoice-returns/(?P<pk>[\d]+)/?$', 
        views.SalesInvoiceReturnsDetailView.as_view(), 
        name='sales-invoice-returns'),
    re_path(r'^sales-invoice-email/(?P<pk>[\d]+)/?$', 
        views.SalesInvoiceEmailSendView.as_view(), 
        name='sales-invoice-email'),
    re_path(r'^sales-invoice-list/?$', views.SalesInvoiceListView.as_view(), name='sales-invoice-list'),
] + sales_router.urls + credit_note_urls

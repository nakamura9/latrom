from django.urls import re_path
from rest_framework import routers

from invoicing import views

invoice_router = routers.DefaultRouter()
invoice_router.register('api/invoice', views.InvoiceAPIViewSet)

urls = [
    re_path(r'^create-invoice/?$', views.InvoiceCreateView.as_view(), name='create-invoice'),
    re_path(r'^(?P<customer>[\d]+)/create-invoice/?$', views.InvoiceCreateView.as_view(), name='create-invoice'),
    re_path(r'^invoice-detail/(?P<pk>[\d]+)/?$', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    re_path(r'^invoice-list/?$', views.InvoiceListView.as_view(), name='invoice-list'),
    re_path(r'^invoice-update/(?P<pk>[\d]+)/?$', views.InvoiceUpdateView.as_view(), 
        name='invoice-update'),
    re_path(r'^invoice-payment/(?P<pk>[\d]+)/?$', views.InvoicePaymentView.as_view(), 
        name='invoice-payment'),
    re_path(r'^invoice-payment-detail/(?P<pk>[\d]+)/?$', views.InvoicePaymentDetailView.as_view(), 
        name='invoice-payment-detail'),
    re_path(r'^invoice-pdf/(?P<pk>[\d]+)/?$', views.InvoicePDFView.as_view(), 
        name='invoice-pdf'),
    re_path(r'^invoice-email/(?P<pk>[\d]+)/?$', views.InvoiceEmailSendView.as_view(), 
        name='invoice-email'),
    re_path(r'^invoice-payment-detail/(?P<pk>[\d]+)/?$', views.InvoicePaymentDetailView.as_view(), 
        name='invoice-payment-detail'),
    re_path(r'^draft-update/(?P<pk>[\d]+)/?$', 
        views.InvoiceDraftUpdateView.as_view(), name='draft-update'),
    re_path(r'^draft-delete/(?P<pk>[\d]+)/?$', 
        views.InvoiceDraftDeleteView.as_view(), name='draft-delete'),
    
] + invoice_router.urls 

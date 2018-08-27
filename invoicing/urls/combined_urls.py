from django.urls import re_path
from invoicing import views
from rest_framework import routers

combined_invoice_router = routers.DefaultRouter()
combined_invoice_router.register('api/combined-invoice', views.CombinedInvoiceAPIViewSet)

combined_urls = [
    re_path(r'^create-combined-invoice/?$', views.CombinedInvoiceCreateView.as_view(), name='create-combined-invoice'),
    re_path(r'^combined-invoice-detail/(?P<pk>[\d]+)/?$', views.CombinedInvoiceDetailView.as_view(), name='combined-invoice-detail'),
    re_path(r'^combined-invoice-list/?$', views.CombinedInvoiceListView.as_view(), name='combined-invoice-list'),
    re_path(r'^combined-invoice-update/(?P<pk>[\d]+)/?$', views.CombinedInvoiceUpdateView.as_view(), 
        name='combined-invoice-update'),
    re_path(r'^combined-invoice-payment/(?P<pk>[\d]+)/?$', views.CombinedInvoicePaymentView.as_view(), 
        name='combined-invoice-payment'),
    re_path(r'^combined-invoice-payment-detail/(?P<pk>[\d]+)/?$', views.CombinedInvoicePaymentDetailView.as_view(), 
        name='combined-invoice-payment-detail'),
    re_path(r'^combined-invoice-pdf/(?P<pk>[\d]+)/?$', views.CombinedInvoicePDFView.as_view(), 
        name='combined-invoice-pdf'),
    re_path(r'^combined-invoice-email/(?P<pk>[\d]+)/?$', views.CombinedInvoiceEmailSendView.as_view(), 
        name='combined-invoice-email'),
    re_path(r'^combined-invoice-payment-detail/(?P<pk>[\d]+)/?$', views.CombinedInvoicePaymentDetailView.as_view(), 
        name='combined-invoice-payment-detail'),
    re_path(r'^combined-draft-update/(?P<pk>[\d]+)/?$', 
        views.CombinedInvoiceDraftUpdateView.as_view(), name='combined-draft-update'),
    
] + combined_invoice_router.urls 


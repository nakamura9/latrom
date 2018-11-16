from django.urls import re_path
from rest_framework.routers import DefaultRouter

from invoicing import views

service_router = DefaultRouter()
service_router.register('api/service-invoice', views.ServiceInvoiceAPIViewSet)

service_urls = [
    re_path(r'^create-service-invoice/?$', views.ServiceInvoiceCreateView.as_view(), name='create-service-invoice'),
    re_path(r'^(?P<customer>[\d]+)/create-service-invoice/?$', views.ServiceInvoiceCreateView.as_view(), name='create-service-invoice'),
    re_path(r'^service-invoice-detail/(?P<pk>[\d]+)/?$', views.ServiceInvoiceDetailView.as_view(), 
        name='service-invoice-detail'),
    re_path(r'^service-invoice-update/(?P<pk>[\d]+)/?$', views.ServiceInvoiceUpdateView.as_view(), 
        name='service-invoice-update'),
    re_path(r'^service-invoice-payment/(?P<pk>[\d]+)/?$', views.ServiceInvoicePaymentView.as_view(), 
        name='service-invoice-payment'),
    re_path(r'^service-invoice-payment-detail/(?P<pk>[\d]+)/?$', views.ServiceInvoicePaymentDetailView.as_view(), 
        name='service-invoice-payment-detail'),
    re_path(r'^service-invoice-pdf/(?P<pk>[\d]+)/?$', views.ServiceInvoicePDFView.as_view(), 
        name='service-invoice-pdf'),
    re_path(r'^service-invoice-email/(?P<pk>[\d]+)/?$', views.ServiceInvoiceEmailSendView.as_view(), 
        name='service-invoice-email'),
    re_path(r'^service-invoice-payment-detail/(?P<pk>[\d]+)/?$', views.ServiceInvoicePaymentDetailView.as_view(), 
        name='service-invoice-payment-detail'),
    re_path(r'^service-draft-update/(?P<pk>[\d]+)/?$', 
        views.ServiceDraftUpdateView.as_view(), name='service-draft-update'),
    re_path(r'^service-draft-delete/(?P<pk>[\d]+)/?$', 
        views.ServiceInvoiceDraftDeleteView.as_view(), name='service-draft-delete'),
    re_path(r'^service-invoice-list/?$', views.ServiceInvoiceListView.as_view(), name='service-invoice-list'),
] + service_router.urls

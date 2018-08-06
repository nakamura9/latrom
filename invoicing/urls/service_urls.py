from django.conf.urls import url
from invoicing import views
from rest_framework.routers import DefaultRouter


service_router = DefaultRouter()
service_router.register('api/service-invoice', views.ServiceInvoiceAPIViewSet)

service_urls = [
    url(r'^create-service-invoice/?$', views.ServiceInvoiceCreateView.as_view(), name='create-service-invoice'),
    url(r'^service-invoice-detail/(?P<pk>[\d]+)/?$', views.ServiceInvoiceDetailView.as_view(), 
        name='service-invoice-detail'),
    url(r'^service-invoice-update/(?P<pk>[\d]+)/?$', views.ServiceInvoiceUpdateView.as_view(), 
        name='service-invoice-update'),
    url(r'^service-invoice-payment/(?P<pk>[\d]+)/?$', views.ServiceInvoicePaymentView.as_view(), 
        name='service-invoice-payment'),
    url(r'^service-invoice-payment-detail/(?P<pk>[\d]+)/?$', views.ServiceInvoicePaymentDetailView.as_view(), 
        name='service-invoice-payment-detail'),
    url(r'^service-draft-update/(?P<pk>[\d]+)/?$', 
        views.ServiceDraftUpdateView.as_view(), name='service-draft-update'),
    url(r'^service-invoice-list/?$', views.ServiceInvoiceListView.as_view(), name='service-invoice-list'),
] + service_router.urls
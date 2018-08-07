from django.conf.urls import url
from invoicing import views
from rest_framework.routers import DefaultRouter

bill_router = DefaultRouter()
bill_router.register('api/bill', views.BillAPIViewSet)

bill_urls = [
    url(r'^create-bill/?$', views.BillCreateView.as_view(), name='bill-create'),
    url(r'^bill-detail/(?P<pk>[\d]+)/?$', views.BillDetailView.as_view(), name='bill-details'),
    url(r'^bill-draft-update/(?P<pk>[\d]+)/?$', views.BillDraftUpdateView.as_view(), name='bill-draft-update'),
    url(r'^bill-update/(?P<pk>[\d]+)/?$', views.BillUpdateView.as_view(), name='bill-update'),
    url(r'^bill-list/?$', views.BillListView.as_view(), name='bills-list'),
    url(r'^bill-payment/(?P<pk>[\d]+)/?$', views.BillPaymentView.as_view(), 
        name='bill-payment'),
    url(r'^bill-payment-detail/(?P<pk>[\d]+)/?$', views.BillPaymentDetailView.as_view(), 
        name='bill-payment-detail'),
    url(r'^bill-pdf/(?P<pk>[\d]+)/?$', views.BillPDFView.as_view(), 
        name='bill-pdf'),
    url(r'^bill-email/(?P<pk>[\d]+)/?$', views.BillEmailSendView.as_view(), 
        name='bill-email'),
    url(r'^bill-payment-detail/(?P<pk>[\d]+)/?$', views.BillPaymentDetailView.as_view(), 
        name='bill-payment-detail'),
] + bill_router.urls

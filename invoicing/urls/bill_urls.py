from django.urls import re_path
from rest_framework.routers import DefaultRouter

from invoicing import views

bill_router = DefaultRouter()
bill_router.register('api/bill', views.BillAPIViewSet)

bill_urls = [
    re_path(r'^create-bill/?$', views.BillCreateView.as_view(), name='bill-create'),
    re_path(r'^bill-detail/(?P<pk>[\d]+)/?$', views.BillDetailView.as_view(), name='bill-details'),
    re_path(r'^bill-draft-update/(?P<pk>[\d]+)/?$', views.BillDraftUpdateView.as_view(), name='bill-draft-update'),
    re_path(r'^bill-update/(?P<pk>[\d]+)/?$', views.BillUpdateView.as_view(), name='bill-update'),
    re_path(r'^bill-list/?$', views.BillListView.as_view(), name='bills-list'),
    re_path(r'^bill-payment/(?P<pk>[\d]+)/?$', views.BillPaymentView.as_view(), 
        name='bill-payment'),
    re_path(r'^bill-payment-detail/(?P<pk>[\d]+)/?$', views.BillPaymentDetailView.as_view(), 
        name='bill-payment-detail'),
    re_path(r'^bill-pdf/(?P<pk>[\d]+)/?$', views.BillPDFView.as_view(), 
        name='bill-pdf'),
    re_path(r'^bill-email/(?P<pk>[\d]+)/?$', views.BillEmailSendView.as_view(), 
        name='bill-email'),
] + bill_router.urls

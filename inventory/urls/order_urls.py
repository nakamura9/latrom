from django.urls import re_path
from rest_framework import routers

from inventory import views

order_router = routers.DefaultRouter()
order_router.register(r'^api/order', views.OrderAPIView)
order_item_router = routers.DefaultRouter()
order_item_router.register(r'^api/order-item', views.OrderItemAPIView)

order_urls = [
    re_path(r'^order-create/?$', views.OrderCreateView.as_view(), 
        name="order-create"),
    re_path(r'^(?P<supplier>[\w]+)/order-create/?$', views.OrderCreateView.as_view(), 
        name="order-create"),
    re_path(r'^order-list/?$', views.OrderListView.as_view(), 
        name="order-list"),
    re_path(r'^order-update/(?P<pk>[\w]+)/?$', views.OrderUpdateView.as_view(), 
        name="order-update"),
    re_path(r'^order-pdf/(?P<pk>[\w]+)/?$', views.OrderPDFView.as_view(), 
        name="order-pdf"),
    re_path(r'^order-email/(?P<pk>[\w]+)/?$', 
        views.OrderEmailSendView.as_view(), name="order-email"),
    re_path(r'^order-delete/(?P<pk>[\w]+)/?$', views.OrderDeleteView.as_view(), 
        name="order-delete"),
    re_path(r'^order-status/(?P<pk>[\w]+)/?$', views.OrderStatusView.as_view(), 
        name="order-status"),
    re_path(r'^order-detail/(?P<pk>[\w]+)/?$', views.OrderDetailView.as_view(), 
        name="order-detail"),
    re_path(r'^order-payment/(?P<pk>[\w]+)/?$', views.OrderPaymentCreateView.as_view(), 
        name="order-payment"),
    re_path(r'^order-payment-list/(?P<pk>[\w]+)/?$', views.OrderPaymentDetailView.as_view(), 
        name="order-payment-list"),
    re_path(r'^order/(?P<pk>[\d]+)/verify/?$',
        views.verify_order, name='verify-order'),
    re_path(r'^order-expense/(?P<pk>[\w]+)/?$', views.ShippingAndHandlingView.as_view(), 
        name="order-expense"),
    re_path(r'^order/expense/list/(?P<pk>[\d]+)/?$',
        views.ShippingCostDetailView.as_view(), name='order-expense-list'),
    re_path(r'^debit-note/create/(?P<pk>[\d]+)/?$', 
        views.DebitNoteCreateView.as_view(), name='debit-note-create'),
    re_path(r'^debit-note/list/(?P<pk>[\d]+)/?$', 
        views.DebitNoteListView.as_view(), name='debit-note-list'),
    re_path(r'^debit-note/detail/(?P<pk>[\d]+)/?$', 
        views.DebitNoteDetailView.as_view(), name='debit-note-detail'),
    re_path(r'^debit-note/pdf/(?P<pk>[\d]+)/?$', 
        views.DebitNotePDFView.as_view(), name='debit-note-pdf')
] + order_router.urls + order_item_router.urls 

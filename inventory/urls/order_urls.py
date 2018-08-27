from django.urls import re_path
from inventory import views
from rest_framework import routers

order_router = routers.DefaultRouter()
order_router.register(r'^api/order', views.OrderAPIView)
order_item_router = routers.DefaultRouter()
order_item_router.register(r'^api/order-item', views.OrderItemAPIView)

order_urls = [
    re_path(r'^order-create/?$', views.OrderCreateView.as_view(), 
        name="order-create"),
    re_path(r'^order-list/?$', views.OrderListView.as_view(), name="order-list"),
    re_path(r'^order-update/(?P<pk>[\w]+)/?$', views.OrderUpdateView.as_view(), 
        name="order-update"),
    re_path(r'^order-pdf/(?P<pk>[\w]+)/?$', views.OrderPDFView.as_view(), 
        name="order-pdf"),
    re_path(r'^order-email/(?P<pk>[\w]+)/?$', views.OrderEmailSendView.as_view(), 
        name="order-email"),
    re_path(r'^order-delete/(?P<pk>[\w]+)/?$', views.OrderDeleteView.as_view(), 
        name="order-delete"),
    re_path(r'^order-status/(?P<pk>[\w]+)/?$', views.OrderStatusView.as_view(), 
        name="order-status"),
    re_path(r'^order-detail/(?P<pk>[\w]+)/?$', views.OrderDetailView.as_view(), 
        name="order-detail"),
] + order_router.urls + order_item_router.urls 
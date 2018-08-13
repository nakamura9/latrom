from django.conf.urls import url
from inventory import views
from rest_framework import routers

order_router = routers.DefaultRouter()
order_router.register(r'^api/order', views.OrderAPIView)
order_item_router = routers.DefaultRouter()
order_item_router.register(r'^api/order-item', views.OrderItemAPIView)

order_urls = [
    url(r'^order-create/?$', views.OrderCreateView.as_view(), 
        name="order-create"),
    url(r'^order-list/?$', views.OrderListView.as_view(), name="order-list"),
    url(r'^order-update/(?P<pk>[\w]+)/?$', views.OrderUpdateView.as_view(), 
        name="order-update"),
    url(r'^order-pdf/(?P<pk>[\w]+)/?$', views.OrderPDFView.as_view(), 
        name="order-pdf"),
    url(r'^order-email/(?P<pk>[\w]+)/?$', views.OrderEmailSendView.as_view(), 
        name="order-email"),
    url(r'^order-delete/(?P<pk>[\w]+)/?$', views.OrderDeleteView.as_view(), 
        name="order-delete"),
    url(r'^order-status/(?P<pk>[\w]+)/?$', views.OrderStatusView.as_view(), 
        name="order-status"),
    url(r'^order-detail/(?P<pk>[\w]+)/?$', views.OrderDetailView.as_view(), 
        name="order-detail"),
] + order_router.urls + order_item_router.urls 
from django.conf.urls import url
from inventory import views 
from rest_framework import routers


transfer_urls = [
    url(r'^create-transfer-order/?$', views.TransferOrderCreateView.as_view(), 
        name='create-transfer-order'),
    url(r'^transfer-order-list/?$', views.TransferOrderListView.as_view(), 
        name='transfer-order-list'),
    url(r'^transfer-order-detail/(?P<pk>[\d]+)/?$', 
        views.TransferOrderDetailView.as_view(), name='transfer-order-detail'),
    url(r'^receive-transfer/(?P<pk>[\d]+)/?$', 
        views.TransferOrderReceiveView.as_view(), name='receive-transfer'),
]

from django.urls import re_path
from rest_framework import routers

from inventory import views

transfer_urls = [
    re_path(r'^create-transfer-order/(?P<pk>[\d]+)/?$', 
        views.TransferOrderCreateView.as_view(), name='create-transfer-order'),
    re_path(r'^transfer-order-list/(?P<pk>[\d]+)/?$', 
        views.TransferOrderListView.as_view(), name='transfer-order-list'),
    re_path(r'^transfer-order-detail/(?P<pk>[\d]+)/?$', 
        views.TransferOrderDetailView.as_view(), name='transfer-order-detail'),
    re_path(r'^receive-transfer/(?P<warehouse>[\d]+)/(?P<pk>[\d]+)/?$', 
        views.TransferOrderReceiveView.as_view(), name='receive-transfer'),
    re_path(r'^api/transfer-order/(?P<pk>[\d]+)/?$', 
        views.TransferOrderAPIView.as_view()),
]

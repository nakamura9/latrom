from django.urls import re_path
from rest_framework import routers

from inventory import views

transfer_urls = [
    re_path(r'^create-transfer-order/(?P<pk>[\d]+)/?$', 
        views.TransferOrderCreateView.as_view(), name='create-transfer-order'),
    re_path(r'^incoming-transfer-order-list/(?P<pk>[\d]+)/?$', 
        views.IncomingTransferOrderListView.as_view(), 
        name='incoming-transfer-order-list'),
    re_path(r'^outgoing-transfer-order-list/(?P<pk>[\d]+)/?$', 
        views.OutgoingTransferOrderListView.as_view(), 
        name='outgoing-transfer-order-list'),
    re_path(r'^transfer-order-detail/(?P<pk>[\d]+)/?$', 
        views.TransferOrderDetailView.as_view(), name='transfer-order-detail'),
    re_path(r'^receive-transfer/(?P<pk>[\d]+)/(?P<warehouse>[\d]+)/?$', 
        views.TransferOrderReceiveView.as_view(), name='receive-transfer'),
    re_path(r'^api/transfer-order/(?P<pk>[\d]+)/?$', 
        views.TransferOrderAPIView.as_view()),
]

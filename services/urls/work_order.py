from django.urls import re_path
from rest_framework import routers

from services import views

worder_router = routers.DefaultRouter()
worder_router.register('api/work-order', views.WorkOrderViewSet)

worder_urls = [
    re_path(r'^work-order-create/(?P<pk>\d+)/?$', views.WorkOrderCreateView.as_view(), 
        name='work-order-create'),
    re_path(r'^work-order-update/(?P<pk>\d+)/?$', 
        views.WorkOrderUpdateView.as_view(), name='work-order-update'),
    re_path(r'^work-order-list/?$', views.WorkOrderListView.as_view(), 
        name='work-order-list'),
    re_path(r'^work-order-complete/(?P<pk>\d+)/?$', 
        views.WorkOrderCompleteView.as_view(), name='work-order-complete'),
    re_path(r'^work-order-authorize/(?P<pk>\d+)/?$', 
        views.work_order_authorize, name='work-order-authorize'),
    re_path(r'^work-order-detail/(?P<pk>\d+)/?$', 
        views.WorkOrderDetailView.as_view(), name='work-order-detail'),
    re_path(r'^work-order/(?P<pk>\d+)/expense-create/?$', 
        views.WorkOrderExpenseCreateView.as_view(), 
        name='work-order-expense-create'),
    re_path(r'^work-order/request/list/?$', 
        views.WorkOrderRequestListView.as_view(),
        name='work-order-request-list'),
    re_path(r'^work-order/request/create/?$', 
        views.WorkOrderRequestCreateView.as_view(), name='work-order-request-create'),
    re_path(r'^work-order/request/(?P<pk>[\d]+)/?$', 
        views.WorkOrderRequestDetailView.as_view(), name='work-order-request-detail'),
    re_path(r'^work-order/costing/(?P<pk>[\d]+)/?$', 
        views.WorkOrderCostingView.as_view(), name='work-order-costing'),
    re_path(r'^work-order/costing-pdf/(?P<pk>[\d]+)/?$', 
        views.WorkOrderCostingPDFView.as_view(), name='work-order-costing-pdf'),

] + worder_router.urls

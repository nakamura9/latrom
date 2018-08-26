from django.conf.urls import url
from services import views
from rest_framework import routers


worder_router = routers.DefaultRouter()
worder_router.register('api/work-order', views.WorkOrderViewSet)

worder_urls = [
    url(r'^work-order-create/?$', views.WorkOrderCreateView.as_view(), 
        name='work-order-create'),
    url(r'^work-order-update/(?P<pk>\d+)/?$', 
        views.WorkOrderUpdateView.as_view(), name='work-order-update'),
    url(r'^work-order-list/?$', views.WorkOrderListView.as_view(), 
        name='work-order-list'),
    url(r'^work-order-complete/(?P<pk>\d+)/?$', 
        views.WorkOrderCompleteView.as_view(), name='work-order-complete'),
    url(r'^work-order-authorize/(?P<pk>\d+)/?$', 
        views.work_order_authorize, name='work-order-authorize'),
    url(r'^work-order-detail/(?P<pk>\d+)/?$', 
        views.WorkOrderDetailView.as_view(), name='work-order-detail'),
] + worder_router.urls


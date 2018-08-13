from django.conf.urls import url
from inventory import views 
from rest_framework import routers

warehouse_router = routers.DefaultRouter()
warehouse_router.register(r'^api/warehouse', views.WareHouseAPIView)

warehouse_urls = [
    url(r'^warehouse-create/$', views.WareHouseCreateView.as_view(), 
        name='warehouse-create'),
    url(r'^warehouse-update/(?P<pk>[\w]+)/?$', 
        views.WareHouseUpdateView.as_view(), name='warehouse-update'),
    url(r'^warehouse-list/$', views.WareHouseListView.as_view(), 
        name='warehouse-list'),
    url(r'^warehouse-detail/(?P<pk>[\w]+)/?$', 
        views.WareHouseDetailView.as_view(), name='warehouse-detail'),
    url(r'^warehouse-delete/(?P<pk>[\w]+)/?$', 
        views.WareHouseDeleteView.as_view(), name='warehouse-delete'),
    url(r'^api/warehouse-items/(?P<warehouse>[\d]+)/?$', 
        views.WareHouseItemListAPIView.as_view(), name='warehouse-items'),
    url(r'^api/warehouse-item/(?P<pk>[\d]+)/?$', 
        views.WareHouseItemAPIView.as_view(), name='warehouse-item'),
    url(r'^api/unpaginated-warehouse-items/(?P<warehouse>[\d]+)/?$', 
        views.UnpaginatedWareHouseItemListAPIView.as_view(), 
    name='unpaginated-warehouse-items'),
]  +  warehouse_router.urls


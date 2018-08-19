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
    url(r'^storage-media-detail/(?P<pk>[\w]+)/?$', 
        views.StorageMediaDetailView.as_view(), name='storage-media-detail'),
    url(r'^storage-media-update/(?P<pk>[\w]+)/?$', 
        views.StorageMediaUpdateView.as_view(), name='storage-media-update'),
    url(r'^storage-media-create/(?P<pk>[\w]+)/?$',
        views.StorageMediaCreateView.as_view(), name='storage-media-create'),
    url(r'^storage-media-list/(?P<pk>[\w]+)/?$',
        views.StorageMediaListView.as_view(), name='storage-media-list'),
    url(r'^api/storage-media/(?P<pk>[\w]+)/?$', 
        views.StorageMediaListAPIView.as_view()),
    url(r'^api/storage-media/?$', 
        views.StorageMediaListAPIView.as_view())
    
]  +  warehouse_router.urls


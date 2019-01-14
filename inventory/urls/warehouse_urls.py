from django.urls import re_path
from rest_framework import routers

from inventory import views

warehouse_router = routers.DefaultRouter()
warehouse_router.register(r'^api/warehouse', views.WareHouseAPIView)

api_urls = [
    re_path(r'^api/warehouse-items/(?P<warehouse>[\d]+)/?$', 
        views.WareHouseItemListAPIView.as_view(), name='warehouse-items'),
    re_path(r'^generate-storage-media/(?P<warehouse>[\d]+)/?$', 
        views.AutogenerateStorageMediaView.as_view(), name='generate-storage-media'),
    re_path(r'^api/warehouse-item/(?P<pk>[\d]+)/?$', 
        views.WareHouseItemAPIView.as_view(), name='warehouse-item'),
    re_path(r'^api/unpaginated-warehouse-items/(?P<warehouse>[\d]+)/?$', 
        views.UnpaginatedWareHouseItemListAPIView.as_view(), 
    name='unpaginated-warehouse-items'),
    re_path(r'^api/storage-media/(?P<pk>[\w]+)/?$', 
        views.StorageMediaListAPIView.as_view()),
    re_path(r'^api/storage-media-nested/(?P<pk>[\w]+)/?$', 
        views.StorageMediaNestedListAPIView.as_view()),
    re_path(r'^api/storage-media-detail/(?P<pk>[\w]+)/?$', 
        views.StorageMediaRetrieveAPIView.as_view()),
]

warehouse_urls = [
    re_path(r'^warehouse-create/$', views.WareHouseCreateView.as_view(), 
        name='warehouse-create'),
    re_path(r'^warehouse-update/(?P<pk>[\w]+)/?$', 
        views.WareHouseUpdateView.as_view(), name='warehouse-update'),
    re_path(r'^warehouse-list/$', views.WareHouseListView.as_view(), 
        name='warehouse-list'),
    re_path(r'^warehouse/(?P<pk>[\w]+)/item-list/?$',   
        views.WareHouseItemListView.as_view(), 
        name='warehouse-item-list'),
    re_path(r'^warehouse-detail/(?P<pk>[\w]+)/?$', 
        views.WareHouseDetailView.as_view(), name='warehouse-detail'),
    re_path(r'^warehouse-delete/(?P<pk>[\w]+)/?$', 
        views.WareHouseDeleteView.as_view(), name='warehouse-delete'),
    re_path(r'^storage-media-detail/(?P<pk>[\w]+)/?$', 
        views.StorageMediaDetailView.as_view(), name='storage-media-detail'),
    re_path(r'^storage-media-update/(?P<pk>[\w]+)/?$', 
        views.StorageMediaUpdateView.as_view(), name='storage-media-update'),
    re_path(r'^storage-media-create/(?P<pk>[\w]+)/?$',
        views.StorageMediaCreateView.as_view(), name='storage-media-create'),
    re_path(r'^storage-media-list/(?P<pk>[\w]+)/?$',
        views.StorageMediaListView.as_view(), name='storage-media-list'),
]  +  warehouse_router.urls + api_urls

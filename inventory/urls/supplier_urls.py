from django.urls import re_path
from inventory import views 
from rest_framework import routers

supplier_urls = [
    re_path(r'^supplier-create/?$', views.SupplierCreateView.as_view(), 
        name="supplier-create"),
    re_path(r'^supplier-list/?$', views.SupplierListView.as_view(), 
        name="supplier-list"),
    re_path(r'^api/supplier/?$', views.SupplierListAPIView.as_view(), 
        name="api-supplier-list"),
    re_path(r'^supplier-update/(?P<pk>[\w]+)/?$', 
        views.SupplierUpdateView.as_view(), name="supplier-update"),
    re_path(r'^supplier-delete/(?P<pk>[\w]+)/?$', 
        views.SupplierDeleteView.as_view(), name="supplier-delete"),        
]
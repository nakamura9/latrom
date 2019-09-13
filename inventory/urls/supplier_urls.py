from django.urls import re_path, path
from rest_framework import routers

from inventory import views

supplier_urls = [
    re_path(r'^supplier/create/?$', 
        views.SupplierCreateView.as_view(),name="supplier-create"),
    path('supplier/import-from-excel/', 
        views.ImportSuppliersView.as_view(),name="import-suppliers-from-excel"),
    path('supplier/create-multiple/', 
        views.CreateMultipleSuppliersView.as_view(),
        name="create-multiple-suppliers"),
    re_path(r'^supplier/list/?$', views.SupplierListView.as_view(),
        name="supplier-list"),
    re_path(r'^api/supplier/?$', 
        views.SupplierListAPIView.as_view(), 
        name="api-supplier-list"),
    re_path(r'^supplier-update/(?P<pk>[\w]+)/?$', 
        views.SupplierUpdateView.as_view(), 
        name="supplier-update"),
    re_path(r'^supplier-detail/(?P<pk>[\w]+)/?$', 
        views.SupplierDetailView.as_view(), 
        name="supplier-detail"),
    re_path(r'^supplier-delete/(?P<pk>[\w]+)/?$', 
        views.SupplierDeleteView.as_view(), 
        name="supplier-delete"), 
    re_path(r'^supplier/add-member/(?P<pk>[\w]+)/?$', 
        views.AddSupplierIndividualView.as_view(), 
        name="supplier-add-member"),        
]

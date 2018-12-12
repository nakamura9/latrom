from django.urls import re_path
from rest_framework import routers

from inventory import views

supplier_urls = [
    re_path(r'^supplier-create/individual/?$', 
        views.IndividualSupplierCreateView.as_view(),name="individual-supplier-create"),
    re_path(r'^supplier-create/organization/?$', 
        views.OrganizationSupplierCreateView.as_view(),name="organization-supplier-create"),
    re_path(r'^supplier-list/individual/?$', views.IndividualSupplierListView.as_view(),
        name="individual-supplier-list"),
    re_path(r'^supplier-list/organization/?$', views.OrganizationSupplierListView.as_view(),
        name="organization-supplier-list"),
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
]

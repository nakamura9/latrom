from django.conf.urls import url
from inventory import views 
from rest_framework import routers


supplier_urls = [
    url(r'^supplier-create/?$', views.SupplierCreateView.as_view(), 
        name="supplier-create"),
    url(r'^supplier-list/?$', views.SupplierListView.as_view(), 
        name="supplier-list"),
    url(r'^supplier-update/(?P<pk>[\w]+)/?$', 
        views.SupplierUpdateView.as_view(), name="supplier-update"),
    url(r'^supplier-delete/(?P<pk>[\w]+)/?$', 
        views.SupplierDeleteView.as_view(), name="supplier-delete"),        
]
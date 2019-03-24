from django.urls import re_path, path
from rest_framework import routers

from inventory import views

item_router = routers.DefaultRouter()
item_router.register(r'^api/inventory-item', views.InventoryItemAPIView)

inventory_item_urls = [
    re_path(r'^product-list/?$', views.InventoryItemListView.as_view(), name="product-list"),
    re_path(r'^product-detail/(?P<pk>[\w]+)/?$', 
        views.InventoryItemDetailView.as_view(), 
        name="product-detail"),
    re_path(r'^product-delete/(?P<pk>[\w]+)/?$', views.InventoryItemDeleteView.as_view(), 
        name="product-delete"),
    path('item-selection', views.ItemSelectionPage.as_view(), name='item-selection')
] + item_router.urls
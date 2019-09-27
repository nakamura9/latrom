from django.urls import re_path, path
from rest_framework import routers

from inventory import views

product_router = routers.DefaultRouter()
product_router.register(r'^api/product', views.ProductAPIView)

product_urls = [
    re_path(r'^product-create/?$', views.ProductCreateView.as_view(), name="product-create"),
    re_path(r'^product-list/?$', views.ProductListView.as_view(), name="product-list"),
    re_path(r'^product-update/(?P<pk>[\w]+)/?$', views.ProductUpdateView.as_view(), 
        name="product-update"),
    re_path(r'^product-detail/(?P<pk>[\w]+)/?$', views.ProductDetailView.as_view(), 
        name="product-detail"),
    re_path(r'^product-delete/(?P<pk>[\w]+)/?$', views.ProductDeleteView.as_view(), 
        name="product-delete")
] + product_router.urls


consumable_router = routers.DefaultRouter()
consumable_router.register(r'^api/consumable', views.ConsumableAPIView)

consumable_urls = [
    re_path(r'^consumable-create/?$', views.ConsumableCreateView.as_view(), name="consumable-create"),
    re_path(r'^consumable-list/?$', views.ConsumableListView.as_view(), name="consumable-list"),
    re_path(r'^consumable-update/(?P<pk>[\w]+)/?$', views.ConsumableUpdateView.as_view(), 
        name="consumable-update"),
    re_path(r'^consumable-detail/(?P<pk>[\w]+)/?$', views.ConsumableDetailView.as_view(), 
        name="consumable-detail"),
] + consumable_router.urls


raw_material_router = routers.DefaultRouter()
raw_material_router.register(r'^api/raw-material', views.RawMaterialAPIView)

raw_material_urls = [
    re_path(r'^raw-material-create/?$', views.RawMaterialCreateView.as_view(), name="raw-material-create"),
    re_path(r'^raw-material-list/?$', views.RawMaterialListView.as_view(), name="raw-material-list"),
    re_path(r'^raw-material-update/(?P<pk>[\w]+)/?$', views.RawMaterialUpdateView.as_view(), 
        name="raw-material-update"),
    re_path(r'^raw-material-detail/(?P<pk>[\w]+)/?$', views.RawMaterialDetailView.as_view(), 
        name="raw-material-detail"),
] + raw_material_router.urls


equipment_router = routers.DefaultRouter()
equipment_router.register(r'^api/equipment', views.EquipmentAPIView)

equipment_urls = [
    re_path(r'^equipment-create/?$', views.EquipmentCreateView.as_view(), 
        name="equipment-create"),
    re_path(r'^equipment-and-consumables-purchase/?$', 
        views.EquipmentandConsumablesPurchaseView.as_view(), 
        name="equipment-and-consumables-purchase"),
    re_path(r'^equipment-list/?$', views.EquipmentListView.as_view(), 
        name="equipment-list"),
    re_path(r'^equipment-update/(?P<pk>[\w]+)/?$', 
        views.EquipmentUpdateView.as_view(), name="equipment-update"),
    re_path(r'^equipment-detail/(?P<pk>[\w]+)/?$', 
        views.EquipmentDetailView.as_view(), name="equipment-detail"),
] + equipment_router.urls

item_urls = [
    path('import-items-from-excel/', views.ImportItemsView.as_view(), 
        name='import-items-from-excel'),
    path('create-multiple-items/', views.BulkCreateItemsView.as_view(), 
        name='create-multiple-items'),
    path('api/items-excluding-products/', 
        views.ItemsExcludingProducts.as_view(),
    )
] +product_urls + equipment_urls + consumable_urls + raw_material_urls

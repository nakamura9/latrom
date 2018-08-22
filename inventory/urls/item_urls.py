from django.conf.urls import url
from inventory import views 
from rest_framework import routers

product_router = routers.DefaultRouter()
product_router.register(r'^api/product', views.ProductAPIView)

product_urls = [
    url(r'^product-create/?$', views.ProductCreateView.as_view(), name="product-create"),
    url(r'^quick-product/?$', views.QuickProductCreateView.as_view(), 
        name="quick-product"),
    url(r'^product-list/?$', views.ProductListView.as_view(), name="product-list"),
    url(r'^product-update/(?P<pk>[\w]+)/?$', views.ProductUpdateView.as_view(), 
        name="product-update"),
    url(r'^product-detail/(?P<pk>[\w]+)/?$', views.ProductDetailView.as_view(), 
        name="product-detail"),
    url(r'^product-delete/(?P<pk>[\w]+)/?$', views.ProductDeleteView.as_view(), 
        name="product-delete")
] + product_router.urls


consumable_router = routers.DefaultRouter()
consumable_router.register(r'^api/consumable', views.ConsumableAPIView)

consumable_urls = [
    url(r'^consumable-create/?$', views.ConsumableCreateView.as_view(), name="consumable-create"),
    url(r'^consumable-list/?$', views.ConsumableListView.as_view(), name="consumable-list"),
    url(r'^consumable-update/(?P<pk>[\w]+)/?$', views.ConsumableUpdateView.as_view(), 
        name="consumable-update"),
    url(r'^consumable-detail/(?P<pk>[\w]+)/?$', views.ConsumableDetailView.as_view(), 
        name="consumable-detail"),
] + consumable_router.urls


equipment_router = routers.DefaultRouter()
equipment_router.register(r'^api/equipment', views.EquipmentAPIView)

equipment_urls = [
    url(r'^equipment-create/?$', views.EquipmentCreateView.as_view(), name="equipment-create"),
    url(r'^equipment-list/?$', views.EquipmentListView.as_view(), name="equipment-list"),
    url(r'^equipment-update/(?P<pk>[\w]+)/?$', 
        views.EquipmentUpdateView.as_view(), name="equipment-update"),
    url(r'^equipment-detail/(?P<pk>[\w]+)/?$', 
        views.EquipmentDetailView.as_view(), name="equipment-detail"),
] + equipment_router.urls

item_urls = product_urls + equipment_urls + consumable_urls

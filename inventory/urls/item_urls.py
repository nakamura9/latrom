from django.conf.urls import url
from inventory import views 
from rest_framework import routers

item_router = routers.DefaultRouter()
item_router.register(r'^api/item', views.ItemAPIView)

item_urls = [
    url(r'^item-create/?$', views.ItemCreateView.as_view(), name="item-create"),
    url(r'^quick-item/?$', views.QuickItemCreateView.as_view(), 
        name="quick-item"),
    url(r'^item-list/?$', views.ItemListView.as_view(), name="item-list"),
    url(r'^item-update/(?P<pk>[\w]+)/?$', views.ItemUpdateView.as_view(), 
        name="item-update"),
    url(r'^item-detail/(?P<pk>[\w]+)/?$', views.ItemDetailView.as_view(), 
        name="item-detail"),
    url(r'^item-delete/(?P<pk>[\w]+)/?$', views.ItemDeleteView.as_view(), 
        name="item-delete")
] + item_router.urls

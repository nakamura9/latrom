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

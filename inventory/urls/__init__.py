from django.urls import re_path
from inventory import views
from .item_urls import item_urls
from .inventory_management_urls import inventory_management_urls
from .warehouse_urls import warehouse_urls
from .order_urls import order_urls
from .report_urls import report_urls 
from .supplier_urls import supplier_urls
from .transfer_urls import transfer_urls
from .item import inventory_item_urls
from rest_framework.routers import DefaultRouter

unit_router = DefaultRouter()
unit_router.register('api/unit', views.UnitAPIView)


urlpatterns = [
    re_path(r'^$', views.InventoryDashboard.as_view(), name="home"),
    re_path(r'^async-dashboard/$', views.AsyncDashboard.as_view(), name="async-dashboard"),
    re_path(r'^unit-create/?$', views.UnitCreateView.as_view(), name="unit-create"),
    re_path(r'^unit-list/?$', views.UnitListView.as_view(), name="unit-list"),
    re_path(r'^unit-update/(?P<pk>\d+)/?$', views.UnitUpdateView.as_view(), name="unit-update"),
    re_path(r'^unit-detail/(?P<pk>\d+)/?$', views.UnitDetailView.as_view(), name="unit-detail"),
    re_path(r'^category-create/?$', views.CategoryCreateView.as_view(), 
        name="category-create"),
    re_path(r'^category-list/?$', views.CategoryListView.as_view(), 
        name="category-list"),
    re_path(r'^category-update/(?P<pk>[\d]+)/?$', views.CategoryUpdateView.as_view(), 
        name="category-update"),
    re_path(r'^category-detail/(?P<pk>[\d]+)/?$', views.CategoryDetailView.as_view(), 
        name="category-detail"),
    re_path(r'api/category/?', views.CategoryListAPIView.as_view()),
    re_path(r'^config/(?P<pk>[\d]+)/?$', views.ConfigView.as_view(), name="config"),
    re_path(r'^inventory-controller-list/?$', 
        views.InventoryControllerListView.as_view(), 
            name='inventory-controller-list'),
    re_path(r'^create-inventory-controller/?$', 
        views.InventoryControllerCreateView.as_view(), 
            name='create-inventory-controller'),
    re_path(r'^update-inventory-controller/(?P<pk>[\d]+)/?$', 
        views.InventoryControllerUpdateView.as_view(), 
            name='update-inventory-controller'),
] 
urlpatterns += item_urls
urlpatterns += inventory_management_urls
urlpatterns += warehouse_urls
urlpatterns += order_urls
urlpatterns += report_urls
urlpatterns += transfer_urls
urlpatterns += supplier_urls
urlpatterns += unit_router.urls
urlpatterns += inventory_item_urls
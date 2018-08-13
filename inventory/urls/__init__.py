from django.conf.urls import url
from inventory import views
from item_urls import item_urls
from inventory_management_urls import inventory_management_urls
from warehouse_urls import warehouse_urls
from order_urls import order_urls
from report_urls import report_urls 
from supplier_urls import supplier_urls
from transfer_urls import transfer_urls

urlpatterns = [
    url(r'^$', views.InventoryDashboard.as_view(), name="home"),
    url(r'^unit-create/?$', views.UnitCreateView.as_view(), name="unit-create"),
    url(r'^category-create/?$', views.CategoryCreateView.as_view(), 
        name="category-create"),
    url(r'^config/(?P<pk>[\d]+)/?$', views.ConfigView.as_view(), name="config"),
    url(r'^inventory-controller-list/?$', 
        views.InventoryControllerListView.as_view(), 
            name='inventory-controller-list'),
    url(r'^create-inventory-controller/?$', 
        views.InventoryControllerCreateView.as_view(), 
            name='create-inventory-controller'),
] 
urlpatterns += item_urls
urlpatterns += inventory_management_urls
urlpatterns += warehouse_urls
urlpatterns += order_urls
urlpatterns += report_urls
urlpatterns += transfer_urls
urlpatterns += supplier_urls
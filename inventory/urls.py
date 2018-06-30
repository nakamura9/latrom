from django.conf.urls import url
import views 
from rest_framework import routers

item_router = routers.DefaultRouter()
item_router.register(r'^api/item', views.ItemAPIView)
order_router = routers.DefaultRouter()
order_router.register(r'^api/order', views.OrderAPIView)
order_item_router = routers.DefaultRouter()
order_item_router.register(r'^api/order-item', views.OrderItemAPIView)

urlpatterns = [
    url(r'^$', views.InventoryHome.as_view(), name="home"),
    url(r'^supplier-create/?$', views.SupplierCreateView.as_view(), name="supplier-create"),
    url(r'^unit-create/?$', views.UnitCreateView.as_view(), name="unit-create"),
    url(r'^category-create/?$', views.CategoryCreateView.as_view(), name="category-create"),
    url(r'^supplier-list/?$', views.SupplierListView.as_view(), name="supplier-list"),
    url(r'^supplier-update/(?P<pk>[\w]+)/?$', views.SupplierUpdateView.as_view(), name="supplier-update"),
    url(r'^supplier-delete/(?P<pk>[\w]+)/?$', views.SupplierDeleteView.as_view(), name="supplier-delete"),
    url(r'^item-create/?$', views.ItemCreateView.as_view(), name="item-create"),
    url(r'^quick-item/?$', views.QuickItemCreateView.as_view(), name="quick-item"),
    url(r'^item-list/?$', views.ItemListView.as_view(), name="item-list"),
    url(r'^item-update/(?P<pk>[\w]+)/?$', views.ItemUpdateView.as_view(), name="item-update"),
    url(r'^item-detail/(?P<pk>[\w]+)/?$', views.ItemDetailView.as_view(), name="item-detail"),
    url(r'^item-delete/(?P<pk>[\w]+)/?$', views.ItemDeleteView.as_view(), name="item-delete"),
    url(r'^order-create/?$', views.OrderCreateView.as_view(), name="order-create"),
    url(r'^order-list/?$', views.OrderListView.as_view(), name="order-list"),
    url(r'^order-update/(?P<pk>[\w]+)/?$', views.OrderUpdateView.as_view(), name="order-update"),
    url(r'^order-delete/(?P<pk>[\w]+)/?$', views.OrderDeleteView.as_view(), name="order-delete"),
    url(r'^order-status/(?P<pk>[\w]+)/?$', views.OrderStatusView.as_view(), name="order-status"),
    url(r'^order-detail/(?P<pk>[\w]+)/?$', views.OrderDetailView.as_view(), name="order-detail"),
    url(r'^stock-receipt-create/?$', views.StockReceiptCreateView.as_view(), name="stock-receipt-create"),
    url(r'^receive-from-order/(?P<pk>[\w]+)/?$', views.create_stock_receipt_from_order, name="receive-from-order"),
    url(r'^config/?$', views.ConfigView.as_view(), name="config"),
] + item_router.urls + order_router.urls + order_item_router.urls
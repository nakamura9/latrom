from django.conf.urls import url
import views 
import report_views
from rest_framework import routers

item_router = routers.DefaultRouter()
item_router.register(r'^api/item', views.ItemAPIView)
order_router = routers.DefaultRouter()
order_router.register(r'^api/order', views.OrderAPIView)
order_item_router = routers.DefaultRouter()
order_item_router.register(r'^api/order-item', views.OrderItemAPIView)
warehouse_router = routers.DefaultRouter()
warehouse_router.register(r'^api/warehouse', views.WareHouseAPIView)
stock_adjustment_router = routers.DefaultRouter()
stock_adjustment_router.register(r'^api/stock-adjustment', views.StockAdjustmentAPIView)


report_urls = [
    url(r'^inventory-report/?$', report_views.InventoryReport.as_view(),    
        name='inventory-report'),
    url(r'^outstanding-orders-report/?$', 
        report_views.OutstandingOrderReport.as_view(),    
            name='outstanding-orders-report')
]

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
    url(r'^goods-received/(?P<pk>[\w]+)/?$', views.GoodsReceivedVoucherView.as_view(), name="goods-received"),
    url(r'^config/?$', views.ConfigView.as_view(), name="config"),
    url(r'^warehouse-create/$', views.WareHouseCreateView.as_view(), name='warehouse-create'),
    url(r'^warehouse-update/(?P<pk>[\w]+)/?$', views.WareHouseUpdateView.as_view(), name='warehouse-update'),
    url(r'^warehouse-list/$', views.WareHouseListView.as_view(), name='warehouse-list'),
    url(r'^warehouse-detail/(?P<pk>[\w]+)/?$', views.WareHouseDetailView.as_view(), name='warehouse-detail'),
    url(r'^warehouse-delete/(?P<pk>[\w]+)/?$', views.WareHouseDeleteView.as_view(), name='warehouse-delete'),
    url(r'^inventory-check/(?P<inventory_check>[\d]+)/(?P<warehouse>[\d]+)/?$', views.InventoryCheckView.as_view(), name='inventory-check'),
    url(r'^inventory-check-form/?$', views.InventoryCheckCreateView.as_view(), name='inventory-check-form'),
    url(r'^inventory-check-list/?$', views.InventoryCheckListView.as_view(), name='inventory-check-list'),
    url(r'^inventory-check-summary/(?P<pk>[\w]+)/?$', views.InventoryCheckDetailView.as_view(), name='inventory-check-summary'),
    url(r'^api/warehouse-items/(?P<warehouse>[\d]+)/?$', views.WareHouseItemListAPIView.as_view(), name='warehouse-items'),
    url(r'^create-transfer-order/?$', views.TransferOrderCreateView.as_view(), name='create-transfer-order'),

] + item_router.urls + order_router.urls + order_item_router.urls + \
    report_urls +  warehouse_router.urls + stock_adjustment_router.urls

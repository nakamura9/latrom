from django.conf.urls import url
from inventory import views 
from rest_framework import routers


stock_adjustment_router = routers.DefaultRouter()
stock_adjustment_router.register(r'^api/stock-adjustment', views.StockAdjustmentAPIView)


inventory_management_urls = [
    url(r'^stock-receipt-create/(?P<pk>[\d]+)/?$', 
        views.StockReceiptCreateView.as_view(), name="stock-receipt-create"),
    url(r'^goods-received/(?P<pk>[\w]+)/?$', 
        views.GoodsReceivedVoucherView.as_view(), name="goods-received"),
    url(r'^create-inventory-check/(?P<pk>[\w]+)/?$', 
        views.InventoryCheckCreateView.as_view(), 
            name='create-inventory-check'),
    url(r'^inventory-check-list/(?P<pk>[\w]+)/?$', views.InventoryCheckListView.as_view(), 
        name='inventory-check-list'),
    url(r'^inventory-check-summary/(?P<pk>[\w]+)/?$', 
        views.InventoryCheckDetailView.as_view(), 
            name='inventory-check-summary'),
    url(r'^scrap-inventory/(?P<pk>[\w]+)/?$', 
        views.ScrappingRecordCreateView.as_view(), 
            name='scrap-inventory'),
    url(r'^scrap-history/(?P<pk>[\w]+)/?$', 
        views.ScrappingReportListView.as_view(), 
            name='scrap-history'),
    url(r'^scrapping-report/(?P<pk>[\w]+)/?$', 
        views.ScrappingReportDetailView.as_view(), 
            name='scrapping-report'),
] + stock_adjustment_router.urls

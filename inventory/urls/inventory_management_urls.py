from django.urls import re_path
from rest_framework import routers

from inventory import views

stock_adjustment_router = routers.DefaultRouter()
stock_adjustment_router.register(r'^api/stock-adjustment', views.StockAdjustmentAPIView)


inventory_management_urls = [
    re_path(r'^config-wizard', views.ConfigWizard.as_view(), name='config-wizard'),
    re_path(r'^stock-receipt-create/(?P<warehouse>[\d]+)/(?P<pk>[\d]+)/?$', 
        views.StockReceiptCreateView.as_view(), name="stock-receipt-create"),
    re_path(r'^stock-receipts-list/(?P<pk>[\d]+)/?$', 
        views.GoodsReceiptsList.as_view(), name="stock-receipts-list"),
    re_path(r'^goods-received/(?P<pk>[\w]+)/?$', 
        views.GoodsReceivedVoucherView.as_view(), name="goods-received"),
    re_path(r'^goods-received-pdf/(?P<pk>[\w]+)/?$', 
        views.GoodsReceivedVoucherPDFView.as_view(), name="goods-received-pdf"),
    re_path(r'^create-inventory-check/(?P<pk>[\w]+)/?$', 
        views.InventoryCheckCreateView.as_view(), 
            name='create-inventory-check'),
    re_path(r'^inventory-check-list/(?P<pk>[\w]+)/?$', views.InventoryCheckListView.as_view(), 
        name='inventory-check-list'),
    re_path(r'^inventory-check-summary/(?P<pk>[\w]+)/?$', 
        views.InventoryCheckDetailView.as_view(), 
            name='inventory-check-summary'),
    re_path(r'^scrap-inventory/(?P<pk>[\w]+)/?$', 
        views.ScrappingRecordCreateView.as_view(), 
            name='scrap-inventory'),
    re_path(r'^scrap-history/(?P<pk>[\w]+)/?$', 
        views.ScrappingReportListView.as_view(), 
            name='scrap-history'),
    re_path(r'^scrapping-report/(?P<pk>[\w]+)/?$', 
        views.ScrappingReportDetailView.as_view(), 
            name='scrapping-report'),
] + stock_adjustment_router.urls

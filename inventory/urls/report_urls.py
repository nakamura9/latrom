from django.urls import re_path, path

from inventory import views

report_urls = [
    re_path(r'^inventory-report/?$', views.InventoryReport.as_view(),    
        name='inventory-report'),
    re_path(r'^outstanding-orders-report/?$', 
        views.OutstandingOrderReport.as_view(),    
            name='outstanding-orders-report'),
    re_path(r'^inventory-report-pdf/?$', views.InventoryReportPDFView.as_view(),
        name='inventory-report-pdf'),
    re_path(r'^outstanding-orders-report-pdf/?$', 
        views.OutstandingOrderReportPDFView.as_view(),    
            name='outstanding-orders-report-pdf'),
    path('payments-due-report', views.PaymentsDueReportView.as_view(), 
        name='payments-due-report'),
    path('vendor-balance-report', views.VendorBalanceReportView.as_view(), 
        name='vendor-balance-report'),
]

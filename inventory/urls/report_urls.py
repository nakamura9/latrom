from django.urls import re_path
from inventory import report_views


report_urls = [
    re_path(r'^inventory-report/?$', report_views.InventoryReport.as_view(),    
        name='inventory-report'),
    re_path(r'^outstanding-orders-report/?$', 
        report_views.OutstandingOrderReport.as_view(),    
            name='outstanding-orders-report')
]
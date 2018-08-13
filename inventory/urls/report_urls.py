from django.conf.urls import url
from inventory import report_views


report_urls = [
    url(r'^inventory-report/?$', report_views.InventoryReport.as_view(),    
        name='inventory-report'),
    url(r'^outstanding-orders-report/?$', 
        report_views.OutstandingOrderReport.as_view(),    
            name='outstanding-orders-report')
]
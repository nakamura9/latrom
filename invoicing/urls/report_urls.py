from django.urls import re_path
from invoicing import views

report_urls = [
    re_path(r'^(?P<pk>[\w]+)/customer-statement-form/?$', 
        views.CustomerReportFormView.as_view(),
             name='customer-statement-form'),
    re_path(r'^customer-statement-form/?$', 
        views.CustomerReportFormView.as_view(),
             name='customer-statement-form'),
    re_path(r'^customer-statement/?$', views.CustomerStatement.as_view(),
             name='customer-statement'),
    re_path(r'^invoice-aging/?$', views.InvoiceAgingReport.as_view(),
             name='invoice-aging'),
    re_path(r'^sales-report-form/?$', views.SalesReportFormView.as_view(),
             name='sales-report-form'),
    re_path(r'^sales-report/?$', views.SalesReportView.as_view(),
             name='sales-report'),
        
]
from django.urls import re_path, path
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
    re_path(r'^customer-statement-pdf/(?P<start>[\w %]+)/(?P<end>[\w %]+)'
        '/(?P<customer>[\d]+)/?$', 
        views.CustomerStatementPDFView.as_view(),
             name='customer-statement-pdf'),
    re_path(r'^invoice-aging/?$', views.InvoiceAgingReport.as_view(),
             name='invoice-aging'),
    re_path(r'^invoice-aging-pdf/?$', views.InvoiceAgingPDFView.as_view(),
             name='invoice-aging-pdf'),
    re_path(r'^sales-report-form/?$', views.SalesReportFormView.as_view(),
             name='sales-report-form'),
    re_path(r'^sales-report/?$', views.SalesReportView.as_view(),
             name='sales-report'),
    re_path(r'^sales-report-pdf/(?P<start>[\w %]+)/(?P<end>[\w %]+)/?$', 
        views.SalesReportPDFView.as_view(),
             name='sales-report-pdf'),
    path("accounts-receivable-report/", 
        views.AccountsReceivableDetailReportView.as_view(), 
        name="accounts-receivable-report")
]
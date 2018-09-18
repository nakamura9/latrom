from django.urls import re_path
from invoicing import views
from rest_framework.routers import DefaultRouter
from .bill_urls import bill_urls
from .combined_urls import combined_urls
from .service_urls import service_urls
from .sales_urls import sales_urls

report_urls = [
    re_path(r'^customer-statement-form/?$', 
        views.CustomerReportFormView.as_view(),
             name='customer-statement-form'),
    re_path(r'^customer-statement/?$', views.CustomerStatement.as_view(),
             name='customer-statement'),
    re_path(r'^invoice-aging/?$', views.InvoiceAgingReport.as_view(),
             name='invoice-aging'),
]

customer_router = DefaultRouter()
customer_router.register(r'api/customer', views.CustomerAPIViewSet, base_name='customer')


customer_urls = [
    re_path(r'^create-customer$', views.CustomerCreateView.as_view(), name='create-customer'),
    re_path(r'^update-customer/(?P<pk>[\w]+)$', views.CustomerUpdateView.as_view(), name='update-customer'),
    re_path(r'^delete-customer/(?P<pk>[\w]+)$', views.CustomerDeleteView.as_view(), name='delete-customer'),
    re_path(r'^customer-list$', views.CustomerListView.as_view(), name='customers-list'),
] + customer_router.urls

sales_rep_router = DefaultRouter()
sales_rep_router.register(r'api/sales-rep', views.SalesRepsAPIViewSet, base_name='sales-rep')

sales_rep_urls = [
    re_path(r'^create-sales-rep$', views.SalesRepCreateView.as_view(), name='create-sales-rep'),
    re_path(r'^update-sales-rep/(?P<pk>[\w]+)$', views.SalesRepUpdateView.as_view(), name='update-sales-rep'),
    re_path(r'^delete-sales-rep/(?P<pk>[\w]+)$', views.SalesRepDeleteView.as_view(), name='delete-sales-rep'),
    re_path(r'^sales-reps-list$', views.SalesRepListView.as_view(), name='sales-reps-list'),
] + sales_rep_router.urls

urlpatterns = [
    re_path(r'^$', views.Home.as_view(), name="home"),
    re_path(r'^config/(?P<pk>[\d]+)/?$', views.ConfigView.as_view(), name="config"),
    re_path(r'^api/config/(?P<pk>[\d]+)/?$', views.ConfigAPIView.as_view(), name='api-config')
] + report_urls + customer_urls + sales_rep_urls + combined_urls + sales_urls + service_urls + \
    bill_urls

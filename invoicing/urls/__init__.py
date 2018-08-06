from django.conf.urls import url
from invoicing import views, report_views
from rest_framework.routers import DefaultRouter
from bill_urls import bill_urls
from combined_urls import combined_urls
from service_urls import service_urls
from sales_urls import sales_urls

report_urls = [
    url(r'^customer-statement-form/?$', 
        report_views.CustomerReportFormView.as_view(),
             name='customer-statement-form'),
    url(r'^customer-statement/?$', report_views.CustomerStatement.as_view(),
             name='customer-statement'),
    url(r'^invoice-aging/?$', report_views.InvoiceAgingReport.as_view(),
             name='invoice-aging'),
]

customer_router = DefaultRouter()
customer_router.register(r'api/customer', views.CustomerAPIViewSet, base_name='customer')


customer_urls = [
    url(r'^create-customer$', views.CustomerCreateView.as_view(), name='create-customer'),
    url(r'^quick-customer$', views.QuickCustomerCreateView.as_view(), name='quick-customer'),
    url(r'^update-customer/(?P<pk>[\w]+)$', views.CustomerUpdateView.as_view(), name='update-customer'),
    url(r'^delete-customer/(?P<pk>[\w]+)$', views.CustomerDeleteView.as_view(), name='delete-customer'),
    url(r'^customer-list$', views.CustomerListView.as_view(), name='customers-list'),
] + customer_router.urls

sales_rep_router = DefaultRouter()
sales_rep_router.register(r'api/sales-rep', views.SalesRepsAPIViewSet, base_name='sales-rep')

sales_rep_urls = [
    url(r'^create-sales-rep$', views.SalesRepCreateView.as_view(), name='create-sales-rep'),
    url(r'^update-sales-rep/(?P<pk>[\w]+)$', views.SalesRepUpdateView.as_view(), name='update-sales-rep'),
    url(r'^delete-sales-rep/(?P<pk>[\w]+)$', views.SalesRepDeleteView.as_view(), name='delete-sales-rep'),
    url(r'^sales-reps-list$', views.SalesRepListView.as_view(), name='sales-reps-list'),
] + sales_rep_router.urls

urlpatterns = [
    url(r'^$', views.Home.as_view(), name="home"),
    url(r'^config/(?P<pk>[\d]+)/?$', views.ConfigView.as_view(), name="config"),
    url(r'^api/config/(?P<pk>[\d]+)/?$', views.ConfigAPIView.as_view(), name='api-config')
] + report_urls + customer_urls + sales_rep_urls + combined_urls + sales_urls + service_urls + \
    bill_urls

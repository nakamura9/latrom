from django.conf.urls import url
from invoicing import views

combined_urls = [
    url(r'^create-combined-invoice/?$', views.CombinedInvoiceCreateView.as_view(), name='create-combined-invoice'),
    url(r'^combined-invoice-detail/(?P<pk>[\d]+)/?$', views.CombinedInvoiceDetailView.as_view(), name='combined-invoice-detail'),
    url(r'^combined-invoice-list/?$', views.CombinedInvoiceListView.as_view(), name='combined-invoice-list'),
]
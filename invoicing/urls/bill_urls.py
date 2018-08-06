from django.conf.urls import url
from invoicing import views
from rest_framework.routers import DefaultRouter


bill_urls = [
    url(r'^create-bill/?$', views.BillCreateView.as_view(), name='create-bill'),
    url(r'^bill-detail/(?P<pk>[\d]+)/?$', views.BillDetailView.as_view(), name='bill-detail'),
    url(r'^bill-list/?$', views.BillListView.as_view(), name='bill-list'),
]

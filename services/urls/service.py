from django.urls import re_path
from rest_framework import routers

from services import views

service_router = routers.DefaultRouter()
service_router.register('api/service', views.ServiceAPIView)

service_urls = [
    re_path(r'^config-wizard/', views.ConfigWizard.as_view(), name='config-wizard'),
    re_path(r'^create-service/?$', views.ServiceCreateView.as_view(), 
        name='create-service'),
    re_path(r'^list-services/?$', views.ServiceListView.as_view(), 
        name='list-services'),
    re_path(r'^service-update/(?P<pk>[\d]+)/?$', 
        views.ServiceUpdateView.as_view(), name='service-update'),
    re_path(r'^service-detail/(?P<pk>[\d]+)/?$', 
        views.ServiceDetailView.as_view(), name='service-details'),
] + service_router.urls 

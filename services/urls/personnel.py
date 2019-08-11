from django.urls import re_path, path
from rest_framework import routers

from services import views

team_router = routers.DefaultRouter()
team_router.register('api/team', views.ServiceTeamAPIView)

service_person_router = routers.DefaultRouter()
service_person_router.register('api/service-person', views.ServicePersonAPIView)

personnel_urls = [
    re_path(r'^service-person-create/?$', 
        views.ServicePersonCreateView.as_view(), 
        name='service-person-create'),
    re_path(r'^service-person-update/(?P<pk>\d+)/?$', 
        views.ServicePersonUpdateView.as_view(), name='service-person-update'),
    path('service-portal', views.ServicePortalView.as_view() ,name='service-portal'),
    re_path(r'^service-person-dashboard/(?P<pk>\d+)/?$', 
        views.ServicePersonDashboardView.as_view(), 
        name='service-person-dashboard'),
    re_path(r'^service-person-list/?$', views.ServicePersonListView.as_view(), 
        name='service-person-list'),
    re_path(r'^team-create/?$', views.ServiceTeamCreateView.as_view(), 
        name='team-create'),
    re_path(r'^team-update/(?P<pk>\d+)/?$', 
        views.ServiceTeamUpdateView.as_view(), 
        name='team-update'),
    re_path(r'^team-detail/(?P<pk>\d+)/?$', 
        views.ServiceTeamDetailView.as_view(), 
        name='team-detail'),
    re_path(r'^team-list/?$', views.ServiceTeamListView.as_view(), 
        name='team-list'),
] + team_router.urls + service_person_router.urls

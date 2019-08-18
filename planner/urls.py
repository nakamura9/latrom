from django.urls import re_path
from rest_framework.routers import DefaultRouter

from . import views
from .api import get_month, get_week, get_day

event_router = DefaultRouter()
event_router.register(r'^api/event', views.EventAPIViewSet)

api_urls = [
    re_path(r'^api/calendar/month/(?P<year>[\d]+)/(?P<month>[\d]+)/?$', 
        get_month),
    re_path(
        r'^api/calendar/day/(?P<year>[\d]+)/(?P<month>[\d]+)/(?P<day>[\d]+)/?$',
        get_day),
    re_path(
        r'^api/calendar/week/(?P<year>[\d]+)/(?P<month>[\d]+)' \
        '/(?P<day>[\d]+)/?$', get_week),
]

urlpatterns = [
    re_path(r'^calendar/?$', views.ReactCalendar.as_view(), 
        name='calendar'),
    re_path(r'^dashboard/?$', views.PlannerDashboard.as_view(), 
        name='dashboard'),
    re_path(r'^config/(?P<pk>\d+)/?$', views.PlannerConfigUpdateView.as_view(), 
        name='config'),
    re_path(r'^event-detail/(?P<pk>\d+)/?$', views.EventDetailView.as_view(), 
        name='event-detail'),
    re_path(r'^event-update/(?P<pk>\d+)/?$', views.EventUpdateView.as_view(), 
        name='event-update'),
    re_path(r'^event-delete/(?P<pk>\d+)/?$', views.EventDeleteView.as_view(), 
        name='event-delete'),
    re_path(r'^event-complete/(?P<pk>\d+)/?$', 
        views.complete_event, name='event-complete'),
    re_path(r'^event-create/?$', views.EventCreateView.as_view(), 
        name='event-create'),
    re_path(r'^event-list/?$', views.EventListView.as_view(), name='event-list'),
    re_path(r'^agenda/(?P<pk>\d+)/?$', views.AgendaView.as_view(), name='agenda'),
    re_path(r'^api/agenda/(?P<pk>\d+)/?$', views.AgendaAPIView.as_view(), name='agenda-api'),
] + event_router.urls + api_urls

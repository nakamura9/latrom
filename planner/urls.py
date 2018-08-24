from . import views
from .api import get_calendar
from django.conf.urls import url
from rest_framework.routers import DefaultRouter

event_router = DefaultRouter()
event_router.register(r'^api/event', views.EventAPIViewSet)

urlpatterns = [
    url(r'^calendar/?$', views.ReactCalendar.as_view(), 
        name='calendar'),
    url(r'^dashboard/?$', views.PlannerDashboard.as_view(), 
        name='dashboard'),
    url(r'api/calendar/', get_calendar, name='calendar-api'),
    url(r'^config/(?P<pk>\d+)?$', views.PlannerConfigUpdateView.as_view(), 
        name='config'),
    url(r'^event-detail/(?P<pk>\d+)/?$', views.EventDetailView.as_view(), 
        name='event-detail'),
    url(r'^event-update/(?P<pk>\d+)/?$', views.EventUpdateView.as_view(), 
        name='event-update'),
    url(r'event-create', views.EventCreateView.as_view(), name='event-create'),
    url(r'event-list', views.EventListView.as_view(), name='event-list'),
    url(r'agenda', views.AgendaView.as_view(), name='agenda'),
] + event_router.urls
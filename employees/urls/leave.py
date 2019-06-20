from django.urls import re_path, path
from rest_framework import routers

from employees import views

leave_urls = [
    re_path(r'^leave-request/?$', views.LeaveDayRequestView.as_view(),
        name='leave-request'),
    re_path(r'^leave-calendar/*', views.LeaveCalendarView.as_view(),
        name='leave-calendar'),
    re_path(r'^leave-list/?$', views.LeaveRequestList.as_view() ,
        name='leave-list' ),
    re_path(r'^leave-detail/(?P<pk>[\d]+)/?$', 
        views.LeaveDayDetailView.as_view() ,
        name='leave-detail'),
    re_path(r'^leave-authorization/(?P<pk>[\d]+)/?$', 
        views.LeaveAuthorizationView.as_view(),
        name='leave-authorization'),
    re_path(r'^api/month/(?P<year>[\d]{4})/(?P<month>[\d]+)', 
        views.get_month_data),
    re_path(r'^api/year/(?P<year>[\d]{4})/?$', 
        views.get_year_data)
    
]


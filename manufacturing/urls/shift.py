from django.urls import path
from manufacturing import views
from rest_framework.routers import DefaultRouter

shift_router = DefaultRouter()
shift_router.register('api/shift', views.ShiftAPIView)

shift_urls = [ 
    path('shift/create', views.ShiftCreateView.as_view(), name='create-shift'),
    path('shift-schedule/create', views.ShiftScheduleCreateView.as_view(), 
        name='create-shift-schedule'),

] + shift_router.urls
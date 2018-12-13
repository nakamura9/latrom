from django.urls import path
from manufacturing import views
from rest_framework.routers import DefaultRouter

shift_router = DefaultRouter()
shift_router.register('api/shift', views.ShiftAPIView)

shift_urls = [ 
    path('shift/create', views.ShiftCreateView.as_view(), name='create-shift'),
    path('shift/list', views.ShiftListView.as_view(), name='list-shift'),
    path('shift-schedule/create', views.ShiftScheduleCreateView.as_view(), 
        name='create-shift-schedule'),
    path('shift-schedule/list', views.ShiftScheduleListView.as_view(), 
        name='shift-schedule-list'),
    path('shift-schedule/detail/<int:pk>', 
        views.ShiftScheduleDetailView.as_view(), 
        name='detail-shift-schedule'),
    path('shift/detail/<int:pk>', 
        views.ShiftDetailView.as_view(), 
        name='detail-shift'),
    path('shift/update/<int:pk>', 
        views.ShiftUpdateView.as_view(), 
        name='update-shift'),

] + shift_router.urls
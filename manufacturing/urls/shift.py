from django.urls import path
from manufacturing import views
shift_urls = [ 
    path('shift/create', views.ShiftCreateView.as_view(), name='create-shift'),
    path('shift-schedule/create', views.ShiftScheduleCreateView.as_view(), 
        name='create-shift-schedule'),

]
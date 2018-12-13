from django.urls import path
from manufacturing import views
from manufacturing.urls.shift import shift_urls
from manufacturing.urls.process import process_urls

urlpatterns = [
    path('', views.Dashboard.as_view() ,name='dashboard'),
] 
urlpatterns += shift_urls
urlpatterns += process_urls
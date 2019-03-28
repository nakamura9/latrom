from django.urls import re_path, path

from employees import views 

portal_urls  = [
    path('portal/login', views.EmployeePortalLogin.as_view(), 
        name='portal-login'),
    path('portal/dashboard/<int:pk>', views.EmployeeDashboard.as_view(),
        name='portal-dashboard')

]
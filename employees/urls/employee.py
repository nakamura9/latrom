from django.urls import re_path, path
from rest_framework import routers

from employees import views

employee_router = routers.DefaultRouter()
employee_router.register(r'^api/employee', views.EmployeeViewSet)


employee_urls = [
    re_path(r'^create-employee/?$', views.EmployeeCreateView.as_view(), 
        name='create-employee'),
    re_path(r'^list-employees/?$', views.EmployeeListView.as_view(), 
        name='list-employees'),
    re_path(r'^employee-update/(?P<pk>[\w]+)/?$', 
        views.EmployeeUpdateView.as_view(), name='employee-update'),
    re_path(r'^employee-portal-update/(?P<pk>[\w]+)/?$', 
        views.EmployeePortalUpdateView.as_view(), name='employee-portal-update'),
    re_path(r'^employee-detail/(?P<pk>[\w]+)/?$', 
        views.EmployeeDetailView.as_view(), name='employee-detail'),
    re_path(r'^employee-delete/(?P<pk>[\w]+)/?$', 
        views.EmployeeDeleteView.as_view(), name='employee-delete'),
    re_path(r'^employee/create-user/(?P<pk>[\w]+)/?$', 
        views.EmployeeUserCreateView.as_view(), name='employee-user-create'),
    re_path(r'^employee/user/reset-password/(?P<pk>[\w]+)/?$', 
        views.EmployeeUserPasswordResetView.as_view(), 
            name='employee-user-password-reset'),
    re_path(r'^employee/delete-user/(?P<pk>[\w]+)/?$', 
        views.remove_employee_user, name='employee-delete-user'),
] + employee_router.urls 
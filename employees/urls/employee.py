from django.urls import re_path, path
from rest_framework import routers

from employees import views

employee_router = routers.DefaultRouter()
employee_router.register(r'^api/employee', views.EmployeeViewSet)

contract_urls = [
    path('create-contract', views.ContractCreateView.as_view(), 
        name='create-contract'),
    path('update-contract/<int:pk>', views.ContractUpdateView.as_view(), 
        name='update-contract'),
    path('contract-details/<int:pk>', views.ContractDetailView.as_view(), 
        name='contract-details'),
    path('terminate-contract/<int:pk>', views.TerminationCreateView.as_view(), 
        name='terminate-contract'),
    path('contract-list', views.ContractListView.as_view(), 
        name='contract-list'),
]

employee_urls = [
    re_path(r'^create-employee/?$', views.EmployeeCreateView.as_view(), 
        name='create-employee'),
    path('create-multiple-employees/', views.CreateMultipleEmployeesView.as_view(), 
        name='create-multiple-employees'),
    path('import-employees-from-excel/', views.ImportEmployeesView.as_view(), 
        name='import-employees-from-excel'),
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
    re_path(r'^employee/user/change-password/(?P<pk>[\w]+)/?$', 
        views.EmployeeUserPasswordChangeView.as_view(), 
            name='employee-user-password-change'),
    re_path(r'^employee/user/reset-password/(?P<pk>[\w]+)/?$', 
            views.EmployeeUserPasswordResetView.as_view(), 
                name='employee-user-password-reset'),
    re_path(r'^employee/delete-user/(?P<pk>[\w]+)/?$', 
        views.remove_employee_user, name='employee-delete-user'),
] + employee_router.urls + contract_urls
from django.urls import re_path, path
from rest_framework import routers

from employees import views

department_router = routers.DefaultRouter()
department_router.register(r'^api/department', views.DepartmentAPIView)


department_urls = [
    path('department/list', views.DepartmentListView.as_view(), name="department-list"),
    path('department/create', views.DepartmentCreateView.as_view(), name="department-create"),
    path('department/detail/<int:pk>', views.DepartmentDetailView.as_view(), name="department-detail"),
    path('department/update/<int:pk>', views.DepartmentUpdateView.as_view(), name="department-update")

] + department_router.urls 
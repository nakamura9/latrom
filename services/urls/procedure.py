from django.urls import re_path
from services import views
from rest_framework import routers


procedure_router = routers.DefaultRouter()
procedure_router.register('api/procedure', views.ProcedureAPIView)

procedure_urls = [
    re_path(r'^create-procedure$', views.ProcedureCreateView.as_view(), name='create-procedure'),
    re_path(r'^list-procedures$', views.ProcedureListView.as_view(), name='list-procedures'),
    re_path(r'^procedure-update/(?P<pk>[\d]+)/$', views.ProcedureUpdateView.as_view(), name='procedure-update'),
    re_path(r'^procedure-detail/(?P<pk>[\d]+)/?$', views.ProcedureDetailView.as_view(), name='procedure-details'),
] + procedure_router.urls

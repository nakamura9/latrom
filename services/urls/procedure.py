from django.urls import re_path
from rest_framework import routers

from services import views

procedure_router = routers.DefaultRouter()
procedure_router.register('api/procedure', views.ProcedureAPIView)

procedure_urls = [
    re_path(r'^create-procedure/?$', views.ProcedureCreateView.as_view(), name='create-procedure'),
    re_path(r'^list-procedures/?$', views.ProcedureListView.as_view(), name='list-procedures'),
    re_path(r'^procedure-update/(?P<pk>[\d]+)/?$', views.ProcedureUpdateView.as_view(), name='procedure-update'),
    re_path(r'^procedure-detail/(?P<pk>[\d]+)/?$', views.ProcedureDetailView.as_view(), name='procedure-details'),
    re_path(r'^procedure-document/(?P<pk>[\d]+)/?$', views.ProcedureDocumentView.as_view(), name='procedure-document'),
    re_path(r'^procedure-document-pdf/(?P<pk>[\d]+)/?$', views.ProcedureDocumentPDFView.as_view(), name='procedure-pdf'),
] + procedure_router.urls

from django.conf.urls import url
from services import views
from rest_framework import routers


procedure_router = routers.DefaultRouter()
procedure_router.register('api/procedure', views.ProcedureAPIView)

procedure_urls = [
    url(r'^create-procedure$', views.ProcedureCreateView.as_view(), name='create-procedure'),
    url(r'^list-procedures$', views.ProcedureListView.as_view(), name='list-procedures'),
    url(r'^procedure-update/(?P<pk>[\d]+)/$', views.ProcedureUpdateView.as_view(), name='procedure-update'),
    url(r'^procedure-detail/(?P<pk>[\d]+)/?$', views.ProcedureDetailView.as_view(), name='procedure-details'),
] + procedure_router.urls

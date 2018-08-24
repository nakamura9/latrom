from django.conf.urls import url
from . import views
from rest_framework import routers

service_router = routers.DefaultRouter()
service_router.register('api/service', views.ServiceAPIView)

service_urls = [
    url(r'^create-service$', views.ServiceCreateView.as_view(), name='create-service'),
    url(r'^list-services$', views.ServiceListView.as_view(), name='list-services'),
    url(r'^service-update/(?P<pk>[\d]+)/$', views.ServiceUpdateView.as_view(), name='service-update'),
    url(r'^service-detail/(?P<pk>[\d]+)/?$', views.ServiceDetailView.as_view(), name='service-details'),
] + service_router.urls 

procedure_router = routers.DefaultRouter()
procedure_router.register('api/procedure', views.ProcedureAPIView)

procedure_urls = [
    url(r'^create-procedure$', views.ProcedureCreateView.as_view(), name='create-procedure'),
    url(r'^list-procedures$', views.ProcedureListView.as_view(), name='list-procedures'),
    url(r'^procedure-update/(?P<pk>[\d]+)/$', views.ProcedureUpdateView.as_view(), name='procedure-update'),
    url(r'^procedure-detail/(?P<pk>[\d]+)/?$', views.ProcedureDetailView.as_view(), name='procedure-details'),
] + procedure_router.urls
 
team_router = routers.DefaultRouter()
team_router.register('api/team', views.ServiceTeamAPIView)

service_person_router = routers.DefaultRouter()
service_person_router.register('api/service-person', views.ServicePersonAPIView)

personnel_urls = [
    url(r'^service-person-create/?$', views.ServicePersonCreateView.as_view(), 
        name='service-person-create'),
    url(r'^service-person-update/(?P<pk>\d+)/?$', 
        views.ServicePersonUpdateView.as_view(), name='service-person-update'),
    url(r'^service-person-dashboard/(?P<pk>\d+)/?$', 
        views.ServicePersonDashboardView.as_view(), name='service-person-dashboard'),
    url(r'^service-person-list/?$', views.ServicePersonListView.as_view(), 
        name='service-person-list'),
    url(r'^team-create/?$', views.ServiceTeamCreateView.as_view(), 
        name='team-create'),
    url(r'^team-update/(?P<pk>\d+)/?$', views.ServiceTeamUpdateView.as_view(), 
        name='team-update'),
    url(r'^team-detail/(?P<pk>\d+)/?$', views.ServiceTeamDetailView.as_view(), 
        name='team-detail'),
    url(r'^team-list/?$', views.ServiceTeamListView.as_view(), name='team-list'),
] + team_router.urls + service_person_router.urls

worder_router = routers.DefaultRouter()
worder_router.register('api/work-order', views.WorkOrderViewSet)

worder_urls = [
    url(r'^work-order-create/?$', views.WorkOrderCreateView.as_view(), 
        name='work-order-create'),
    url(r'^work-order-update/(?P<pk>\d+)/?$', 
        views.WorkOrderUpdateView.as_view(), name='work-order-update'),
    url(r'^work-order-list/?$', views.WorkOrderListView.as_view(), 
        name='work-order-list'),
    url(r'^work-order-complete/(?P<pk>\d+)/?$', 
        views.WorkOrderCompleteView.as_view(), name='work-order-complete'),
    url(r'^work-order-authorize/(?P<pk>\d+)/?$', 
        views.work_order_authorize, name='work-order-authorize'),
    url(r'^work-order-detail/(?P<pk>\d+)/?$', 
        views.WorkOrderDetailView.as_view(), name='work-order-detail'),
] + worder_router.urls


urlpatterns = [
    url(r'^$', views.Dashboard.as_view(), name='dashboard')
] + service_urls + procedure_urls

urlpatterns += personnel_urls
urlpatterns += worder_urls 
from django.urls import include, re_path

from common_data import views

urlpatterns = [
    re_path(r'^workflow/?$', views.WorkFlowView.as_view(), name="workflow"),
    re_path(r'^react-test/?$', views.ReactTest.as_view(), name="react-test"),
    re_path(r'^api/config/?$', views.config_JSON_API, name='api-config'),
    re_path(r'^logo-re_path/?$', views.get_logo_url, name='logo-re_path'),
    re_path(r'^organization/create/?$', views.OrganizationCreateView.as_view(), 
        name='organization-create'),
    re_path(r'^organization/list/?$', views.OrganizationListView.as_view(), 
        name='organization-list'),
    re_path(r'^organization/update/(?P<pk>[\d]+)/?$', views.OrganizationUpdateView.as_view(), 
        name='organization-update'),
    re_path(r'^organization/detail/(?P<pk>[\d]+)/?$', views.OrganizationDetailView.as_view(), 
        name='organization-detail'),
    re_path(r'^individual/create/?$', views.IndividualCreateView.as_view(), 
        name='individual-create'),
    re_path(r'^individual/list/?$', views.IndividualListView.as_view(), 
        name='individual-list'),
    re_path(r'^individual/update/(?P<pk>[\d]+)/?$', views.IndividualUpdateView.as_view(), 
        name='individual-update'),
    re_path(r'^individual/detail/(?P<pk>[\d]+)/?$', views.IndividualDetailView.as_view(), 
        name='individual-detail'),
    re_path(r'^config/(?P<pk>[\d]+)/?$', views.GlobalConfigView.as_view(), 
        name='config'),
    re_path(r'^email/?$', views.SendEmail.as_view(), 
        name='email'),
]

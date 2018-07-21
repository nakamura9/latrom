from django.conf.urls import url, include
import views
#from crudbuilder import urls

urlpatterns = [
    url(r'^workflow/?$', views.WorkFlowView.as_view(), name="workflow"),
    url(r'^react-test/?$', views.ReactTest.as_view(), name="react-test"),
    url(r'^api/config/?$', views.config_JSON_API, name='api-config'),
    url(r'^logo-url/?$', views.get_logo_url, name='logo-url'),
    url(r'^organization/create/?$', views.OrganizationCreateView.as_view(), 
        name='organization-create'),
    url(r'^organization/list/?$', views.OrganizationListView.as_view(), 
        name='organization-list'),
    url(r'^organization/update/(?P<pk>[\d]+)/?$', views.OrganizationUpdateView.as_view(), 
        name='organization-update'),
    url(r'^organization/detail/(?P<pk>[\d]+)/?$', views.OrganizationDetailView.as_view(), 
        name='organization-detail')  
    #url(r'^crud/', include(urls)),
]
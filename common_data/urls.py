from django.conf.urls import url
import views


urlpatterns = [
    url(r'^workflow/?$', views.WorkFlowView.as_view(), name="workflow"),
    url(r'^react-test/?$', views.ReactTest.as_view(), name="react-test"),
    url(r'^api/config/?$', views.config_JSON_API, name='api-config'),
    url(r'^logo-url/?$', views.get_logo_url, name='logo-url'), 
]
from django.conf.urls import url
import views


urlpatterns = [
    url(r'^test/?$', views.Test.as_view(), name="test"),
    url(r'^react-test/?$', views.ReactTest.as_view(), name="react-test"),    
]
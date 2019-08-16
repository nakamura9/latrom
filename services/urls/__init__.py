from django.urls import re_path
from services import views
from .personnel import personnel_urls
from .procedure import procedure_urls
from .work_order import worder_urls
from .service import service_urls
from .requisition import requisition_urls
from .reports import report_urls
import services

urlpatterns = [
    re_path(r'^$', views.Dashboard.as_view(), name='dashboard'),
    re_path(r'^async-dashboard/?$', views.AsyncDashboard.as_view(), name='async-dashboard'),
    re_path(r'^create-category/?$', views.ServiceCategoryCreateView.as_view(), name='create-category'),
    re_path(r'^update-category/(?P<pk>[\d]+)/?$', views.ServiceCategoryUpdateView.as_view(), name='update-category'),
    re_path(r'^category-detail/(?P<pk>[\d]+)/?$', views.ServiceCategoryDetailView.as_view(), name='category-detail'),
    re_path(r'^category-list/?$', views.ServiceCategoryListView.as_view(), name='category-list')
]



urlpatterns += personnel_urls
urlpatterns += worder_urls 
urlpatterns += service_urls 
urlpatterns += procedure_urls
urlpatterns += requisition_urls
urlpatterns += report_urls
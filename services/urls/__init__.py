from django.conf.urls import url
from services import views
from .personnel import personnel_urls
from .procedure import procedure_urls
from .work_order import worder_urls
from .service import service_urls
from .requisition import requisition_urls

urlpatterns = [
    url(r'^$', views.Dashboard.as_view(), name='dashboard')
]

urlpatterns += personnel_urls
urlpatterns += worder_urls 
urlpatterns += service_urls 
urlpatterns += procedure_urls
urlpatterns += requisition_urls
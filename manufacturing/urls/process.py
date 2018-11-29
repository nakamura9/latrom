from django.urls import path
from manufacturing import views

process_urls = [
    path('process/create', views.ProcessCreateView.as_view() ,name='create-process'),
    path('process-machine/create', views.ProcessMachineCreateView.as_view() ,name='create-process-machine'),
    path('process-product/create', views.ProcessProductCreateView.as_view() ,name='create-process-product'),
    path('production-order/create', views.ProductionOrderCreateView.as_view() , name='create-production-order'),
    path('bill-of-materials/create', views.BillOfMaterialsCreateView.as_view() ,name='create-bill-of-materials'),
] 
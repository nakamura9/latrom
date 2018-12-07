from django.urls import path
from manufacturing import views
from rest_framework.routers import DefaultRouter

process_machine_router = DefaultRouter()
process_machine_router.register('api/process-machine', 
    views.ProcessMachineAPIView)

process_product_router = DefaultRouter()
process_product_router.register('api/process-product', 
    views.ProcessProductAPIView)

process_router = DefaultRouter()
process_router.register('api/process', 
    views.ProcessAPIView)

process_urls = [
    path('process/create', views.ProcessCreateView.as_view() ,name='create-process'),
    path('process-machine/create', views.ProcessMachineCreateView.as_view() ,name='create-process-machine'),
    path('process-rate/create', views.ProcessRateCreateView.as_view() ,name='create-process-rate'),
    path('process-machine-group/create',
        views.ProcessMachineGroupCreateView.as_view(),
        name='create-process-machine-group'),
    path('process-equipment/create', 
        views.ProcessEquipmentCreateView.as_view() ,
        name='create-process-equipment'),
    path('process-product/create', views.ProcessProductCreateView.as_view() ,name='create-process-product'),
    path('process-product-list/create', views.ProcessProductListCreateView.as_view() ,name='create-process-product-list'),
    path('production-order/create', views.ProductionOrderCreateView.as_view() , name='create-production-order'),
    path('bill-of-materials/create', views.BillOfMaterialsCreateView.as_view() ,name='create-bill-of-materials'),
] + process_machine_router.urls + process_product_router.urls + process_router.urls
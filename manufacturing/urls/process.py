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
    path('process/list', views.ProcessListView.as_view() ,name='list-process'),
    path('process/update/<int:pk>', views.ProcessUpdateView.as_view() ,name='update-process'),
    path('process/delete/<int:pk>', views.ProcessDeleteView.as_view() ,name='delete-process'),
    path('process/detail/<int:pk>', views.ProcessDetailView.as_view() ,name='process-detail'),
    path('process/dashboard/<int:pk>', views.ProcessCreateView.as_view() ,name='process-dashboard'),
    path('process-machine/create', views.ProcessMachineCreateView.as_view() ,name='create-process-machine'),
    path('process-machine/list', views.ProcessMachineListView.as_view() ,name='list-process-machine'),
    path('process-machine/update/<int:pk>', views.ProcessMachineUpdateView.as_view() ,name='update-process-machine'),
    path('process-machine/detail/<int:pk>', views.ProcessMachineDetailView.as_view() ,name='detail-process-machine'),
    
    path('process-rate/create', views.ProcessRateCreateView.as_view() ,name='create-process-rate'),
    path('process-machine-group/create',
        views.ProcessMachineGroupCreateView.as_view(),
        name='create-process-machine-group'),
    path('process-machine-group/list',
        views.ProcessMachineGroupListView.as_view(),
        name='list-process-machine-group'),
    path('process-machine-group/detail/<int:pk>',
        views.ProcessMachineGroupDetailView.as_view(),
        name='detail-process-machine-group'),
    
    path('process-product/create', views.ProcessProductCreateView.as_view() ,name='create-process-product'),
    path('process-product/list', views.ProcessProductListView.as_view() ,name='list-process-product'),
    path('process-product-list/create', views.ProcessProductListCreateView.as_view() ,name='create-process-product-list'),
    path('production-order/create', views.ProductionOrderCreateView.as_view() , name='create-production-order'),
    path('production-order/list', views.ProductionOrderListView.as_view() , name='list-production-order'),
    path('bill-of-materials/create', views.BillOfMaterialsCreateView.as_view() ,name='create-bill-of-materials'),
] + process_machine_router.urls + process_product_router.urls + process_router.urls
from django.conf.urls import url
from services import views
from rest_framework import routers


requisition_urls = [
    url(r'^equipment-requisition-create/?$', views.EquipmentRequisitionCreateView.as_view(), name='equipment-requisition-create'),
    url(r'^equipment-requisition-list/?$', views.EquipmentRequisitionListView.as_view(), name='equipment-requisition-list'),
    url(r'^equipment-requisition-detail/(?P<pk>\d+)/?$', views.EquipmentRequisitionDetailView.as_view(), name='equipment-requisition-detail'),
    url(r'^equipment-requisition-release/(?P<pk>\d+)/?$', views.equipment_requisition_release, 
    name='equipment-requisition-release'),
    url(r'^equipment-requisition-authorize/(?P<pk>\d+)/?$', views.equipment_requisition_authorize, name='equipment-requisition-authorize'),
    url(r'^consumable-requisition-create/?$', views.ConsumableRequisitionCreateView.as_view(), name='consumable-requisition-create'),
    url(r'^consumable-requisition-list/?$', views.ConsumableRequisitionListView.as_view(), name='consumable-requisition-list'),
    url(r'^consumable-requisition-detail/(?P<pk>\d+)/?$', views.ConsumableRequisitionDetailView.as_view(), name='consumable-requisition-detail'),
    url(r'^consumable-requisition-release/(?P<pk>\d+)/?$', views.consumable_requisition_release, 
    name='consumable-requisition-release'),
    url(r'^consumable-requisition-authorize/(?P<pk>\d+)/?$', views.consumable_requisition_authorize, name='consumable-requisition-authorize'),
]
from . import models
import django_filters

class ServiceFilter(django_filters.FilterSet):
    class Meta:
        model = models.Service
        fields = {
            'name': ['icontains']
        }

class ProcedureFilter(django_filters.FilterSet):
    class Meta:
        model = models.ServiceProcedure
        fields = {
            'name': ['icontains']
        }

class ServicePersonFilter(django_filters.FilterSet):
    class Meta:
        model = models.ServicePerson
        fields = {
            'employee': ['exact']
        }

class WorkOrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.ServiceWorkOrder
        fields = {
            'date': ['exact'],
            'status': ['exact'],
            'completed': ['exact']
        }

class ConsumableRequisitionFilter(django_filters.FilterSet):
    class Meta:
        model = models.ConsumablesRequisition
        fields = {
            'date': ['exact'],
            'requested_by': ['exact']
        }


class EquipmentRequisitionFilter(django_filters.FilterSet):
    class Meta:
        model = models.ConsumablesRequisition
        fields = {
            'date': ['exact'],
            'requested_by': ['exact']
        }
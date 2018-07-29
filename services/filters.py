import models
import django_filters

class ServiceFilter(django_filters.FilterSet):
    class Meta:
        model = models.Service
        fields = {
            'name': ['icontains']
        }
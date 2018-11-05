from django_filters import FilterSet

from . import models


class EventFilter(FilterSet):
    class Meta:
        model = models.Event
        fields = {
            'date': ['exact'],
            'label': ['icontains'],
            'completed': ['exact']
        }

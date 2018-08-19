from django_filters import FilterSet
import models 

class EventFilter(FilterSet):
    class Meta:
        model = models.Event
        fields = {
            'date': ['exact'],
            'label': ['icontains']
        }

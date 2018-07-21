from django_filters import FilterSet
import models 

class OrganizationFilter(FilterSet):
    class Meta:
        model = models.Organization
        fields = {
            'legal_name': ['exact']
        }
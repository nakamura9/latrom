from django_filters import FilterSet

from common_data import models


class OrganizationFilter(FilterSet):
    class Meta:
        model = models.Organization
        fields = {
            'legal_name': ['icontains']
        }

class IndividualFilter(FilterSet):
    class Meta:
        model = models.Individual
        fields = {
            'first_name': ['icontains'],
            'last_name': ['icontains']
        }

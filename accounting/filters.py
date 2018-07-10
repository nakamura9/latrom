
import django_filters

import models 


class JournalFilter(django_filters.FilterSet):
    class Meta:
        model = models.Journal
        fields = {
            'name': ['icontains'],
        }

class AccountFilter(django_filters.FilterSet):
    class Meta:
        model = models.Account
        fields = {
            'name': ['icontains'],
            'type': ['exact']
        }



import django_filters
from . import models 

class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = models.Customer
        fields = {
            'organization': ['exact'],
            'individual': ['exact'],
            
        }

class AbstractInvoiceFilter(django_filters.FilterSet):
    class Meta:
        model = models.SalesInvoice
        fields = {
            'date': ['icontains'],
            'customer': ['exact'],
            'salesperson': ['exact'],
        }

class SalesRepFilter(django_filters.FilterSet):
    class Meta:
        model = models.SalesRepresentative
        fields = {
            'employee': ['exact'],
        }


class CreditNoteFilter(django_filters.FilterSet):
    class Meta:
        model = models.CreditNote
        fields = {
            'date': ['exact'],
        }

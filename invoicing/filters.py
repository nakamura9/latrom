

import django_filters
import models 

class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = models.Customer
        fields = {
            'name': ['icontains'],
            
        }

class InvoiceFilter(django_filters.FilterSet):
    class Meta:
        model = models.Invoice
        fields = {
            'number': ['icontains'],
            'date_issued': ['icontains'],
            'customer': ['exact'],
            'salesperson': ['exact'],
            'type_of_invoice': ['exact'],
        }

class SalesRepFilter(django_filters.FilterSet):
    class Meta:
        model = models.SalesRepresentative
        fields = {
            'employee': ['exact'],
        }

class PaymentFilter(django_filters.FilterSet):
    class Meta:
        model = models.Payment
        fields = {
            'date': ['exact'],
            'method': ['exact'],
            'sales_rep': ['exact'],
            'reference_number': ['icontains'],
        }


class QuoteFilter(django_filters.FilterSet):
    class Meta:
        model = models.Quote
        fields = {
            'date': ['exact'],
            'number': ['icontains'],
            'customer': ['exact'],
            'salesperson': ['exact'],
        }


class CreditNoteFilter(django_filters.FilterSet):
    class Meta:
        model = models.CreditNote
        fields = {
            'date': ['exact'],
        }

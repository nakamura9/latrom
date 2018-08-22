
from models import *

import django_filters
from django.db import models

class ItemFilter(django_filters.FilterSet):
    
    class Meta:
        model = Product
        fields = {
            'name': ['icontains'],
            'unit': ['exact'],
            'supplier': ['exact'],
            'category': ['exact'],
            }
        

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            'tracking_number': ['icontains'],
            'supplier': ['exact'],
            'status': ['exact'],
            'issue_date': ['exact'],
            'expected_receipt_date': ['exact']
        }

class SupplierFilter(django_filters.FilterSet):
    class Meta:
        model = Supplier
        fields = {
            'organization': ['exact'],
            'individual': ['exact']
        }


class InventoryCheckFilter(django_filters.FilterSet):
    class Meta:
        model = InventoryCheck
        fields = {
            'date': ['exact'],
            'warehouse': ['exact'],
            'adjusted_by': ['exact']
        }


class TransferOrderFilter(django_filters.FilterSet):
    class Meta:
        model = TransferOrder
        fields = {
            'issue_date': ['exact'],
            'source_warehouse': ['exact'],
            'receiving_warehouse': ['exact']
        }

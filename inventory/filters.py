
from models import *

import django_filters
from django.db import models

class ItemFilter(django_filters.FilterSet):
    
    class Meta:
        model = Item
        fields = {
            'item_name': ['icontains'],
            'code': ['icontains'],
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
            'name': ['icontains'],
            'contact_person': ['icontains']
        }

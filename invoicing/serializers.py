from rest_framework import serializers

from .models import *
from inventory.serializers import ItemSerializer
from accounting.serializers import TaxSerializer, ExpenseSerializer


class SalesRepsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRepresentative
        fields = "__all__"
    
class CustomerSerializer(serializers.ModelSerializer):
    expense_set = ExpenseSerializer(many=True)
    class Meta:
        model = Customer
        fields = "__all__"
    


class ConfigSerializer(serializers.ModelSerializer):
    sales_tax = TaxSerializer(many=False)
    class Meta:
        model = SalesConfig
        fields = "__all__"


class SalesInvoiceLineSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False)
    class Meta:
        model = SalesInvoiceLine
        fields = ['item', 'quantity']

class SalesInvoiceSerializer(serializers.ModelSerializer):
    salesinvoiceline_set = SalesInvoiceLineSerializer(many=True)
    class Meta:
        model = SalesInvoice
        fields = '__all__'
from rest_framework import serializers

from .models import *
from inventory.serializers import ItemSerializer
from accounting.serializers import TaxSerializer, ExpenseSerializer
from services.serializers import ServiceSerializer

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
        fields = ['item', 'quantity', 'id']


class SalesInvoiceSerializer(serializers.ModelSerializer):
    salesinvoiceline_set = SalesInvoiceLineSerializer(many=True)
    class Meta:
        model = SalesInvoice
        fields = '__all__'

class ServiceInvoiceLineSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(many=False)
    class Meta:
        model = ServiceInvoiceLine
        fields = "__all__"


class ServiceInvoiceSerializer(serializers.ModelSerializer):
    serviceinvoiceline_set = ServiceInvoiceLineSerializer(many=True)
    class Meta:
        model = ServiceInvoice
        fields = ['serviceinvoiceline_set', 'customer', 'id']

class BillLineSerializer(serializers.ModelSerializer):
    expense = ExpenseSerializer(many=False)
    class Meta:
        model = BillLine
        fields = "__all__"


class BillSerializer(serializers.ModelSerializer):
    billline_set = BillLineSerializer(many=True)
    class Meta:
        model = Bill
        fields = ['billline_set', 'customer', 'id']


class CombinedInvoiceLineSerializer(serializers.ModelSerializer):
    expense = ExpenseSerializer(many=False)
    item = ItemSerializer(many=False)
    service = ServiceSerializer(many=False)
    class Meta:
        model = CombinedInvoiceLine
        fields = "__all__"


class CombinedInvoiceSerializer(serializers.ModelSerializer):
    combinedinvoiceline_set = CombinedInvoiceLineSerializer(many=True)
    class Meta:
        model = CombinedInvoice
        fields = ['combinedinvoiceline_set', 'customer', 'id']



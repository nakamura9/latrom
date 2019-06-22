from rest_framework import serializers

from accounting.serializers import ExpenseSerializer, TaxSerializer
from services.serializers import ServiceSerializer
from inventory.serializers import InventoryItemSerializer

from .models import *


class SalesRepsSerializer(serializers.ModelSerializer):
    rep_name = serializers.SerializerMethodField()
    class Meta:
        model = SalesRepresentative
        fields = "__all__"

    def get_rep_name(self, obj):
        return obj.employee.full_name
    
class CustomerSerializer(serializers.ModelSerializer):
    expense_set = ExpenseSerializer(many=True)

    class Meta:
        model = Customer
        fields = ['name', 'id', 'expense_set', 'organization', 'individual', 'account', 'billing_address', 'banking_details']
    


class ConfigSerializer(serializers.ModelSerializer):
    sales_tax = TaxSerializer(many=False)
    class Meta:
        model = SalesConfig
        fields = "__all__"


class ExpenseLineComponentSerializer(serializers.ModelSerializer):
    expense = ExpenseSerializer(many=False)
    class Meta:
        model = ExpenseLineComponent
        fields = "__all__"

class ProductLineComponentSerializer(serializers.ModelSerializer):
    product = InventoryItemSerializer(many=False)
    returned_quantity = serializers.ReadOnlyField()
    class Meta:
        model = ProductLineComponent
        fields = "__all__"


class ServiceLineComponentSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(many=False)
    class Meta:
        model = ServiceLineComponent
        fields = "__all__"

class InvoiceLineSerializer(serializers.ModelSerializer):
    expense = ExpenseLineComponentSerializer(many=False)
    product = ProductLineComponentSerializer(many=False)
    service = ServiceLineComponentSerializer(many=False)
    tax = TaxSerializer(many=False)
    
    class Meta:
        model = InvoiceLine
        fields = "__all__"

class InvoiceSerializer(serializers.ModelSerializer):
    invoiceline_set = InvoiceLineSerializer(many=True)
    class Meta:
        model = Invoice
        fields = ['invoiceline_set', 'customer', 'id']


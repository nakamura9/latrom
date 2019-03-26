from rest_framework import serializers

from accounting.serializers import ExpenseSerializer, TaxSerializer
from services.serializers import ServiceSerializer
from inventory.serializers import InventoryItemSerializer

from .models import *


class SalesRepsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesRepresentative
        fields = "__all__"
    
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

class SalesInvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesInvoiceLine
        fields = ['product', 'quantity', 'id', 'returned_quantity']


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
    service = ServiceSerializer(many=False)
    class Meta:
        model = CombinedInvoiceLine
        fields = "__all__"


class CombinedInvoiceSerializer(serializers.ModelSerializer):
    combinedinvoiceline_set = CombinedInvoiceLineSerializer(many=True)
    class Meta:
        model = CombinedInvoice
        fields = ['combinedinvoiceline_set', 'customer', 'id']


class ExpenseLineComponentSerializer(serializers.ModelSerializer):
    expense = ExpenseSerializer(many=False)
    class Meta:
        model = ExpenseLineComponent
        fields = "__all__"

class ProductLineComponentSerializer(serializers.ModelSerializer):
    product = InventoryItemSerializer(many=False)
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
    
    class Meta:
        model = InvoiceLine
        fields = "__all__"

class InvoiceSerializer(serializers.ModelSerializer):
    invoiceline_set = InvoiceLineSerializer(many=True)
    class Meta:
        model = Invoice
        fields = ['invoiceline_set', 'customer', 'id']


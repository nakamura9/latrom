from rest_framework import serializers

from .models import *
from accounting.serializers import TaxSerializer
class ProductComponentSerializer(serializers.ModelSerializer):
    tax = TaxSerializer(many=False)
    class Meta:
        model = ProductComponent
        fields = "__all__"

class EquipmentComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentComponent
        fields = "__all__"

class InventoryItemSerializer(serializers.ModelSerializer):
    product_component = ProductComponentSerializer(many=False)
    equipment_component = EquipmentComponentSerializer(many=False)
    unit_sales_price = serializers.ReadOnlyField()
    class Meta:
        model = InventoryItem
        fields = "__all__"

class WareHouseItemSerializer(serializers.ModelSerializer):
    item = InventoryItemSerializer(many=False)
    class Meta:
        model = WareHouseItem
        fields = ['item', 'name', 'id', 'quantity', 'warehouse', 'location']


class WareHouseSerializer(serializers.ModelSerializer):
    warehouseitem_set = WareHouseItemSerializer(many=True)
    class Meta:
        model = WareHouse
        fields = "__all__"

class StockAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockAdjustment
        fields = "__all__"

class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)

    class Meta:
        model = Category
        fields = "__all__"


class StorageMediaSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)
    class Meta:
        model = StorageMedia
        #fields = "__all__"
        exclude = "location",

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = ['id', 'name']








class OrderItemSerializer(serializers.ModelSerializer):
    item = InventoryItemSerializer(many=False)
    unit = UnitSerializer(many=False)
    class Meta:
        fields = "__all__"
        model = OrderItem

class OrderSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True)
    class Meta:
        model = Order
        fields = "__all__"

class TransferOrderLineSerializer(serializers.ModelSerializer):
    item = InventoryItemSerializer(many=False)
    class Meta:
        model = TransferOrderLine
        fields ="__all__"

class TransferOrderSerializer(serializers.ModelSerializer):
    transferorderline_set = TransferOrderLineSerializer(many=True)
    class Meta:
        model = TransferOrder
        fields ="__all__"
from rest_framework import serializers

from .models import *


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['unit_sales_price', 'unit_purchase_price', 'quantity',
            'id', 'name', 'description']

class ConsumableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumable
        fields = ['unit_purchase_price', 'quantity',
            'id', 'name', 'description']

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['unit_purchase_price', 'quantity',
            'id', 'name', 'description']

class WareHouseItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    consumable = ConsumableSerializer(many=False)
    equipment = EquipmentSerializer(many=False)
    
    class Meta:
        model = WareHouseItem
        fields = ['product', 'consumable','equipment','item_type','name', 'id', 'quantity', 'warehouse', 'location']


class WareHouseSerializer(serializers.ModelSerializer):
    warehouseitem_set = WareHouseItemSerializer(many=True)
    class Meta:
        model = WareHouse
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    consumable = ConsumableSerializer(many=False)
    equipment = EquipmentSerializer(many=False)
    
    class Meta:
        fields = "__all__"
        model = OrderItem

class OrderSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True)
    class Meta:
        model = Order
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

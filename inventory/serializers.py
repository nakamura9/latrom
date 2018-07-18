from rest_framework import serializers
from models import *

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['unit_sales_price', 'unit_purchase_price', 'quantity',
            'code', 'item_name', 'description']

class WareHouseItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False)
    class Meta:
        model = WareHouseItem
        fields = "__all__"


class WareHouseSerializer(serializers.ModelSerializer):
    warehouseitem_set = WareHouseItemSerializer(many=True)
    class Meta:
        model = WareHouse
        fields = "__all__"

class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer(many=False)
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
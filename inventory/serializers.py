from rest_framework import serializers
from models import *

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['unit_sales_price', 'unit_purchase_price', 'quantity',
            'code', 'item_name', 'description']

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
from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model  = OrderItem
        fields = ["product_id", "vendor_id", "quantity", "price", "subtotal"]

    def get_subtotal(self, obj):
        return obj.subtotal()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = ["id", "user_id", "status", "total", "created_at", "updated_at", "items"]

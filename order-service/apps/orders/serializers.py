from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OrderItem
        fields = [
            "id",
            "product_id",
            "vendor_id",
            "quantity",
            "unit_price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    # this includes all items inside the order
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = [
            "id",
            "user_id",
            "status",
            "total_amount",
            "stripe_payment_id",
            "items",
            "created_at",
            "updated_at",
        ]


class CreateOrderSerializer(serializers.Serializer):
    """
    Used when creating a new order.
    Expects a list of items from the cart.
    """
    items = serializers.ListField(
        child=serializers.DictField()
    )
    # items format:
    # [
    #   {
    #     "product_id": "uuid",
    #     "vendor_id":  "uuid",
    #     "quantity":   2,
    #     "unit_price": 29.99
    #   }
    # ]


class UpdateOrderStatusSerializer(serializers.Serializer):
    """
    Used when updating order status.
    Only admin or vendor can do this.
    """
    status = serializers.ChoiceField(
        choices=[
            "pending",
            "paid",
            "shipped",
            "delivered",
            "cancelled",
        ]
    )
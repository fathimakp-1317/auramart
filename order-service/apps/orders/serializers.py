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

class CheckoutSerializer(serializers.Serializer):
    """
    Used for the checkout endpoint.
    Takes user_id and processes their cart.
    """
    user_id = serializers.CharField(max_length=255)
    # we get items FROM the cart automatically
    # customer doesn't need to send items again
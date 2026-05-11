from rest_framework import serializers
from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Inventory
        fields = [
            "id",
            "product_id",
            "quantity",
            "version",
            "last_updated",
        ]


class AddInventorySerializer(serializers.Serializer):
    """
    Used when adding a new product to inventory.
    Vendor does this when they list a new product.
    """
    product_id = serializers.CharField(max_length=255)
    quantity   = serializers.IntegerField(min_value=0)


class UpdateInventorySerializer(serializers.Serializer):
    """
    Used when updating stock quantity.
    Only accepts positive numbers.
    """
    quantity = serializers.IntegerField(min_value=0)


class RestockInventorySerializer(serializers.Serializer):
    """
    Used when vendor adds more stock.
    Adds to existing quantity.
    """
    quantity_to_add = serializers.IntegerField(min_value=1)
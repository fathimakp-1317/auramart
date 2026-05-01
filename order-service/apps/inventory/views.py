from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Inventory
from .serializers import (
    InventorySerializer,
    AddInventorySerializer,
    UpdateInventorySerializer,
    RestockInventorySerializer
)


# ─── Add Product to Inventory ─────────────────────────────
@api_view(["POST"])
def add_inventory(request):
    """
    Add a new product to inventory.
    Called when vendor lists a new product.

    Expects:
    {
        "product_id": "uuid",
        "quantity":   100
    }
    """
    serializer = AddInventorySerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "success": False,
            "error": {
                "code":    "VALIDATION_ERROR",
                "message": serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    product_id = serializer.validated_data["product_id"]
    quantity   = serializer.validated_data["quantity"]

    # check if product already in inventory
    if Inventory.objects.filter(
        product_id=product_id
    ).exists():
        return Response({
            "success": False,
            "error": {
                "code":    "ALREADY_EXISTS",
                "message": f"Product {product_id} "
                           f"already in inventory. "
                           f"Use restock endpoint instead."
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    inventory = Inventory.objects.create(
        product_id=product_id,
        quantity=quantity,
        version=0
    )

    return Response({
        "success": True,
        "data":    InventorySerializer(inventory).data
    }, status=status.HTTP_201_CREATED)


# ─── Get Inventory for a Product ──────────────────────────
@api_view(["GET"])
def get_inventory(request, product_id):
    """
    Get current stock level for a product.
    """
    inventory = get_object_or_404(
        Inventory,
        product_id=product_id
    )

    return Response({
        "success": True,
        "data":    InventorySerializer(inventory).data
    })


# ─── Get All Inventory ────────────────────────────────────
@api_view(["GET"])
def get_all_inventory(request):
    """
    Get stock levels for all products.
    Admin use only.
    """
    inventory = Inventory.objects.all().order_by(
        "last_updated"
    )

    return Response({
        "success": True,
        "data": {
            "count":     inventory.count(),
            "inventory": InventorySerializer(
                             inventory,
                             many=True
                         ).data
        }
    })


# ─── Restock Inventory ────────────────────────────────────
@api_view(["PATCH"])
def restock_inventory(request, product_id):
    """
    Add more stock to existing inventory.
    Vendor uses this when they get new stock.

    Expects:
    { "quantity_to_add": 50 }
    """
    inventory = get_object_or_404(
        Inventory,
        product_id=product_id
    )

    serializer = RestockInventorySerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response({
            "success": False,
            "error": {
                "code":    "VALIDATION_ERROR",
                "message": serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    quantity_to_add = serializer.validated_data[
        "quantity_to_add"
    ]

    # use transaction to prevent race conditions
    with transaction.atomic():
        # lock this row until transaction is done
        inventory = Inventory.objects.select_for_update().get(
            product_id=product_id
        )
        old_quantity      = inventory.quantity
        inventory.quantity += quantity_to_add
        inventory.version  += 1
        inventory.save()

    return Response({
        "success": True,
        "data": {
            "product_id":   product_id,
            "old_quantity": old_quantity,
            "added":        quantity_to_add,
            "new_quantity": inventory.quantity,
            "version":      inventory.version
        }
    })


# ─── Reduce Inventory (When Order is Placed) ──────────────
@api_view(["PATCH"])
def reduce_inventory(request, product_id):
    """
    Reduce stock when an order is placed.
    Uses version number to prevent race conditions.

    This is the CRITICAL endpoint for Week 3 testing.
    Two people buying last item = only one succeeds.

    Expects:
    {
        "quantity":        2,
        "current_version": 5
    }
    """
    inventory = get_object_or_404(
        Inventory,
        product_id=product_id
    )

    quantity        = request.data.get("quantity")
    current_version = request.data.get("current_version")

    if not quantity or current_version is None:
        return Response({
            "success": False,
            "error": {
                "code":    "MISSING_FIELDS",
                "message": "quantity and "
                           "current_version are required"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():
        # lock this specific row
        inventory = Inventory.objects.select_for_update().get(
            product_id=product_id
        )

        # check version matches
        # if it doesn't match someone else already
        # updated the inventory before us
        if inventory.version != int(current_version):
            return Response({
                "success": False,
                "error": {
                    "code":    "VERSION_CONFLICT",
                    "message": "Inventory was updated "
                               "by another request. "
                               "Please retry.",
                    "current_version": inventory.version
                }
            }, status=status.HTTP_409_CONFLICT)

        # check if enough stock available
        if inventory.quantity < int(quantity):
            return Response({
                "success": False,
                "error": {
                    "code":    "INSUFFICIENT_STOCK",
                    "message": f"Only {inventory.quantity} "
                               f"items in stock. "
                               f"Requested: {quantity}"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        # all checks passed — reduce the stock
        old_quantity       = inventory.quantity
        inventory.quantity -= int(quantity)
        inventory.version  += 1
        inventory.save()

    return Response({
        "success": True,
        "data": {
            "product_id":   product_id,
            "old_quantity": old_quantity,
            "reduced_by":   int(quantity),
            "new_quantity": inventory.quantity,
            "version":      inventory.version
        }
    })


# ─── Check Stock Availability ─────────────────────────────
@api_view(["GET"])
def check_stock(request, product_id):
    """
    Check if enough stock is available
    before placing an order.

    Returns version number too — needed
    for reduce_inventory call.
    """
    inventory = get_object_or_404(
        Inventory,
        product_id=product_id
    )

    quantity_needed = request.query_params.get(
        "quantity", 1
    )

    is_available = inventory.quantity >= int(quantity_needed)

    return Response({
        "success": True,
        "data": {
            "product_id":       product_id,
            "quantity_needed":  int(quantity_needed),
            "quantity_in_stock":inventory.quantity,
            "is_available":     is_available,
            "version":          inventory.version
            # ⚠️ save this version number
            # you need it when calling reduce_inventory
        }
    })


# ─── Get Low Stock Products ───────────────────────────────
@api_view(["GET"])
def get_low_stock(request):
    """
    Get all products with stock below 10.
    Useful for vendor alerts.
    """
    low_stock = Inventory.objects.filter(
        quantity__lt=10
    ).order_by("quantity")

    return Response({
        "success": True,
        "data": {
            "count":     low_stock.count(),
            "inventory": InventorySerializer(
                             low_stock,
                             many=True
                         ).data
        }
    })
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .redis_cart import (
    get_cart,
    add_to_cart,
    remove_from_cart,
    update_quantity,
    clear_cart
)


@api_view(["GET"])
def view_cart(request, user_id):
    """Get the current cart for a user."""
    cart = get_cart(user_id)
    return Response({
        "success": True,
        "data":    cart
    })


@api_view(["POST"])
def add_item(request, user_id):
    """
    Add an item to the cart.
    Expects: { product_id, quantity, price }
    """
    product_id = request.data.get("product_id")
    quantity   = request.data.get("quantity", 1)
    price      = request.data.get("price")

    if not product_id or not price:
        return Response({
            "success": False,
            "error": {
                "code":    "MISSING_FIELDS",
                "message": "product_id and price are required"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    cart = add_to_cart(user_id, product_id,
                       int(quantity), float(price))
    return Response({
        "success": True,
        "data":    cart
    })


@api_view(["DELETE"])
def remove_item(request, user_id, product_id):
    """Remove a specific item from the cart."""
    cart = remove_from_cart(user_id, product_id)
    return Response({
        "success": True,
        "data":    cart
    })


@api_view(["PATCH"])
def update_item(request, user_id, product_id):
    """
    Update quantity of an item in the cart.
    Expects: { quantity }
    """
    quantity = request.data.get("quantity")

    if quantity is None:
        return Response({
            "success": False,
            "error": {
                "code":    "MISSING_FIELDS",
                "message": "quantity is required"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    cart = update_quantity(user_id, product_id,
                           int(quantity))
    return Response({
        "success": True,
        "data":    cart
    })


@api_view(["DELETE"])
def clear_user_cart(request, user_id):
    """Clear the entire cart for a user."""
    clear_cart(user_id)
    return Response({
        "success": True,
        "data": {
            "message": f"Cart cleared for user {user_id}"
        }
    })
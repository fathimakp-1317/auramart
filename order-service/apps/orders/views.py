from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    CreateOrderSerializer,
    UpdateOrderStatusSerializer
)
from apps.inventory.events import publish_order_completed
from .checkout_service import process_checkout
from .serializers import CheckoutSerializer
import uuid


# ─── Create Order ─────────────────────────────────────────
@api_view(["POST"])
def create_order(request):
    """
    Create a new order.

    Expects:
    {
        "user_id": "uuid",
        "items": [
            {
                "product_id": "uuid",
                "vendor_id":  "uuid",
                "quantity":   2,
                "unit_price": 29.99
            }
        ]
    }
    """
    serializer = CreateOrderSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "success": False,
            "error": {
                "code":    "VALIDATION_ERROR",
                "message": serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    items   = serializer.validated_data["items"]
    user_id = request.data.get("user_id")

    if not user_id:
        return Response({
            "success": False,
            "error": {
                "code":    "MISSING_USER_ID",
                "message": "user_id is required"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    # calculate total amount from items
    total = sum(
        float(item["unit_price"]) * int(item["quantity"])
        for item in items
    )

    # create the order
    order = Order.objects.create(
        user_id=user_id,
        total_amount=round(total, 2),
        status="pending"
    )

    # create each order item
    order_items = []
    for item in items:
        order_item = OrderItem.objects.create(
            order=order,
            product_id=item["product_id"],
            vendor_id=item["vendor_id"],
            quantity=int(item["quantity"]),
            unit_price=float(item["unit_price"])
        )
        order_items.append({
            "product_id": str(item["product_id"]),
            "quantity":   int(item["quantity"])
        })

    # publish order.completed event to RabbitMQ
    # and update user_interactions table for recommendations
    try:
        publish_order_completed(
            order_id=str(order.id),
            user_id=str(user_id),
            items=order_items
        )
    except Exception as e:
        # don't fail the order if RabbitMQ is down
        print(f"RabbitMQ publish failed: {e}")

    return Response({
        "success": True,
        "data":    OrderSerializer(order).data
    }, status=status.HTTP_201_CREATED)


# ─── Get All Orders for a User ────────────────────────────
@api_view(["GET"])
def get_user_orders(request, user_id):
    """
    Get all orders for a specific user.
    Most recent orders come first.
    """
    orders = Order.objects.filter(
        user_id=user_id
    ).order_by("-created_at")

    return Response({
        "success": True,
        "data": {
            "count":  orders.count(),
            "orders": OrderSerializer(orders, many=True).data
        }
    })


# ─── Get Single Order ─────────────────────────────────────
@api_view(["GET"])
def get_order(request, order_id):
    """
    Get details of a specific order.
    """
    order = get_object_or_404(Order, id=order_id)

    return Response({
        "success": True,
        "data":    OrderSerializer(order).data
    })


# ─── Update Order Status ──────────────────────────────────
@api_view(["PATCH"])
def update_order_status(request, order_id):
    """
    Update the status of an order.
    Example: pending → paid → shipped → delivered

    Expects:
    { "status": "shipped" }
    """
    order = get_object_or_404(Order, id=order_id)

    serializer = UpdateOrderStatusSerializer(
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

    order.status = serializer.validated_data["status"]
    order.save()

    return Response({
        "success": True,
        "data":    OrderSerializer(order).data
    })


# ─── Cancel Order ─────────────────────────────────────────
@api_view(["PATCH"])
def cancel_order(request, order_id):
    """
    Cancel an order.
    Only pending orders can be cancelled.
    """
    order = get_object_or_404(Order, id=order_id)

    if order.status != "pending":
        return Response({
            "success": False,
            "error": {
                "code":    "CANNOT_CANCEL",
                "message": f"Cannot cancel order "
                           f"with status: {order.status}"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    order.status = "cancelled"
    order.save()

    return Response({
        "success": True,
        "data": {
            "message":  "Order cancelled successfully",
            "order_id": str(order.id)
        }
    })


# ─── Get All Orders (Admin) ───────────────────────────────
@api_view(["GET"])
def get_all_orders(request):
    """
    Get all orders in the system.
    This is for admin use only.
    """
    orders = Order.objects.all().order_by("-created_at")

    return Response({
        "success": True,
        "data": {
            "count":  orders.count(),
            "orders": OrderSerializer(orders, many=True).data
        }
    })

@api_view(["POST"])
def checkout(request):
    """
    Full checkout flow.

    Steps automatically:
    1. Gets cart from Redis
    2. Checks stock
    3. Creates order
    4. Reduces inventory
    5. Clears cart
    6. Publishes RabbitMQ event

    Expects:
    { "user_id": "uuid" }

    Returns:
    { order_id, total_amount, status, items }
    """
    serializer = CheckoutSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "success": False,
            "error": {
                "code":    "VALIDATION_ERROR",
                "message": serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    user_id = serializer.validated_data["user_id"]

    try:
        order_data = process_checkout(user_id)
        return Response({
            "success": True,
            "data":    order_data
        }, status=status.HTTP_201_CREATED)

    except ValueError as e:
        # stock error or empty cart
        return Response({
            "success": False,
            "error": {
                "code":    "CHECKOUT_FAILED",
                "message": str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code":    "SERVER_ERROR",
                "message": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
from .order_flow import full_order_flow


@api_view(["POST"])
def place_order(request):
    """
    THE MAIN ENDPOINT.
    Single endpoint that does everything:

    1. Gets cart
    2. Checks stock
    3. Creates order
    4. Sets up Stripe payment
    5. Clears cart
    6. Publishes RabbitMQ event

    Returns order + client_secret for payment.

    Expects:
    { "user_id": "uuid" }
    """
    user_id = request.data.get("user_id")

    if not user_id:
        return Response({
            "success": False,
            "error": {
                "code":    "MISSING_USER_ID",
                "message": "user_id is required"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        result = full_order_flow(user_id)
        return Response({
            "success": True,
            "data":    result
        }, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({
            "success": False,
            "error": {
                "code":    "ORDER_FAILED",
                "message": str(e)
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code":    "SERVER_ERROR",
                "message": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
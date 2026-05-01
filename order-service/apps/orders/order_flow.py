"""
Complete Order Flow
===================
This file connects everything together
in the correct sequence.

Flow:
1. Customer adds items to cart (already works)
2. Customer clicks checkout
3. We validate stock
4. We create the order
5. We initiate Stripe payment
6. Customer pays
7. We confirm payment
8. We update order to paid
9. We clear cart
10. We publish RabbitMQ event
"""

from django.db import transaction
from apps.cart.redis_cart import get_cart, clear_cart
from apps.inventory.models import Inventory
from apps.inventory.events import publish_order_completed
from apps.payments.stripe_client import create_payment_intent
from apps.payments.models import Payment
from .models import Order, OrderItem


def full_order_flow(user_id: str) -> dict:
    """
    Complete order flow from cart to payment.

    Returns everything frontend needs:
    - order details
    - stripe client_secret for payment form
    """

    # ── 1. Get Cart ───────────────────────────────────────
    cart = get_cart(user_id)

    if not cart["items"]:
        raise ValueError("Cart is empty. Add items first.")

    # ── 2. Check Stock for Every Item ─────────────────────
    stock_errors = []
    for item in cart["items"]:
        try:
            inventory = Inventory.objects.get(
                product_id=item["product_id"]
            )
            if inventory.quantity < int(item["quantity"]):
                stock_errors.append({
                    "product_id": item["product_id"],
                    "requested":  item["quantity"],
                    "available":  inventory.quantity
                })
        except Inventory.DoesNotExist:
            stock_errors.append({
                "product_id": item["product_id"],
                "error":      "Not found in inventory"
            })

    if stock_errors:
        raise ValueError({
            "code":    "INSUFFICIENT_STOCK",
            "details": stock_errors
        })

    # ── 3. Create Order + Reduce Inventory ────────────────
    with transaction.atomic():

        # calculate total
        total = sum(
            float(i["price"]) * int(i["quantity"])
            for i in cart["items"]
        )

        # create order
        order = Order.objects.create(
            user_id=user_id,
            total_amount=round(total, 2),
            status="pending"
        )

        rabbitmq_items = []

        for item in cart["items"]:
            # create order item
            OrderItem.objects.create(
                order=order,
                product_id=item["product_id"],
                vendor_id=item.get("vendor_id", "unknown"),
                quantity=int(item["quantity"]),
                unit_price=float(item["price"])
            )

            # reduce inventory with lock
            inventory = Inventory.objects.select_for_update().get(
                product_id=item["product_id"]
            )
            inventory.quantity -= int(item["quantity"])
            inventory.version  += 1
            inventory.save()

            rabbitmq_items.append({
                "product_id": item["product_id"],
                "quantity":   int(item["quantity"])
            })

        # ── 4. Create Stripe Payment Intent ───────────────
        try:
            payment_data = create_payment_intent(
                amount=float(order.total_amount),
                order_id=str(order.id)
            )

            # save payment record
            Payment.objects.create(
                order=order,
                stripe_charge_id=payment_data[
                    "payment_intent_id"
                ],
                amount=order.total_amount,
                status="pending"
            )

        except Exception as e:
            # if Stripe fails rollback everything
            raise ValueError(
                f"Payment setup failed: {str(e)}"
            )

    # ── 5. Clear Cart ─────────────────────────────────────
    clear_cart(user_id)

    # ── 6. Publish RabbitMQ Event ─────────────────────────
    try:
        publish_order_completed(
            order_id=str(order.id),
            user_id=str(user_id),
            items=rabbitmq_items
        )
    except Exception as e:
        print(f"RabbitMQ publish failed: {e}")

    # ── 7. Return Everything Frontend Needs ───────────────
    return {
        "order_id":          str(order.id),
        "user_id":           user_id,
        "status":            order.status,
        "total_amount":      float(order.total_amount),
        "items":             rabbitmq_items,
        "payment": {
            "payment_intent_id": payment_data[
                "payment_intent_id"
            ],
            "client_secret":     payment_data[
                "client_secret"
            ],
            # ← frontend uses this to show payment form
            "currency":          "usd"
        },
        "next_step": (
            "Use client_secret to confirm payment "
            "with Stripe on the frontend"
        )
    }
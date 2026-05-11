from django.db import transaction
from apps.cart.redis_cart import get_cart, clear_cart
from apps.inventory.models import Inventory
from apps.inventory.events import publish_order_completed
from .models import Order, OrderItem
from apps.orders.tasks import send_order_confirmation_email
from apps.inventory.tasks import check_low_stock_after_order

def process_checkout(user_id: str) -> dict:
    """
    Full checkout flow in one function.

    Steps:
    1. Get cart from Redis
    2. Validate cart is not empty
    3. Check stock for all items
    4. Create order and order items
    5. Reduce inventory
    6. Clear cart
    7. Publish RabbitMQ event

    Returns order data or raises an exception.
    """

    # ── Step 1: Get Cart ──────────────────────────────────
    cart = get_cart(user_id)

    if not cart["items"]:
        raise ValueError("Cart is empty")

    # ── Step 2: Check Stock for All Items ─────────────────
    stock_errors = []

    for item in cart["items"]:
        product_id = item["product_id"]
        quantity   = item["quantity"]

        try:
            inventory = Inventory.objects.get(
                product_id=product_id
            )
            if inventory.quantity < quantity:
                stock_errors.append({
                    "product_id": product_id,
                    "requested":  quantity,
                    "available":  inventory.quantity
                })
        except Inventory.DoesNotExist:
            stock_errors.append({
                "product_id": product_id,
                "requested":  quantity,
                "available":  0,
                "error":      "Product not found in inventory"
            })

    # if any item has stock issues stop here
    if stock_errors:
        raise ValueError({
            "code":    "INSUFFICIENT_STOCK",
            "details": stock_errors
        })

    # ── Step 3: Create Order (inside transaction) ─────────
    with transaction.atomic():

        # calculate total
        total = sum(
            float(item["price"]) * int(item["quantity"])
            for item in cart["items"]
        )

        # create the order
        order = Order.objects.create(
            user_id=user_id,
            total_amount=round(total, 2),
            status="pending"
        )

        # create order items + reduce inventory
        rabbitmq_items = []

        for item in cart["items"]:
            product_id = item["product_id"]
            quantity   = int(item["quantity"])
            price      = float(item["price"])

            # create order item
            OrderItem.objects.create(
                order=order,
                product_id=product_id,
                vendor_id=item.get(
                    "vendor_id", "unknown"
                ),
                quantity=quantity,
                unit_price=price
            )

            # reduce inventory with row lock
            inventory = Inventory.objects.select_for_update().get(
                product_id=product_id
            )
            inventory.quantity -= quantity
            inventory.version  += 1
            inventory.save()

            rabbitmq_items.append({
                "product_id": product_id,
                "quantity":   quantity
            })

    # ── Step 4: Clear Cart ────────────────────────────────
    # done AFTER transaction so cart only clears
    # if everything succeeded
    clear_cart(user_id)

    # ── Step 5: Publish RabbitMQ Event ────────────────────
    try:
        publish_order_completed(
            order_id=str(order.id),
            user_id=str(user_id),
            items=rabbitmq_items
        )
    except Exception as e:
        # don't fail the order if RabbitMQ is down
        print(f"RabbitMQ publish failed: {e}")
    
    # ── Send Confirmation Email (Background) ──────
    send_order_confirmation_email.delay(
        order_id=str(order.id),
        user_email=f"{user_id}@example.com",
        total_amount=float(order.total_amount),
        items=rabbitmq_items
    )

    # ── Check Stock Levels (Background) ───────────
    for item in rabbitmq_items:
        check_low_stock_after_order.delay(
            product_id=item["product_id"],
            quantity_sold=item["quantity"]
        )

    return {
        "order_id":     str(order.id),
        "user_id":      user_id,
        "total_amount": float(order.total_amount),
        "status":       order.status,
        "items_count":  len(cart["items"]),
        "items":        rabbitmq_items
    }
"""
Celery Tasks for Inventory
===========================
Background tasks related to
inventory management.
"""

from celery import shared_task


# ─── Check Low Stock After Order ─────────────────────────
@shared_task
def check_low_stock_after_order(
    product_id: str,
    quantity_sold: int
):
    """
    Check if stock is low after an order.
    If below 10, trigger low stock alert.

    Called automatically after every order.
    """
    from apps.inventory.models import Inventory

    try:
        inventory = Inventory.objects.get(
            product_id=product_id
        )

        print(
            f"Stock check: {product_id} "
            f"has {inventory.quantity} left"
        )

        # trigger low stock alert if below 10
        if inventory.quantity < 10:
            from apps.orders.tasks import (
                send_low_stock_alert
            )
            # send alert in background
            send_low_stock_alert.delay(
                product_id=product_id,
                current_quantity=inventory.quantity,
                vendor_email="vendor@example.com"
                # in real app get from vendor profile
            )
            print(
                f"⚠️ Low stock alert triggered "
                f"for {product_id}"
            )

        return {
            "product_id": product_id,
            "quantity":   inventory.quantity,
            "alert_sent": inventory.quantity < 10
        }

    except Inventory.DoesNotExist:
        print(f"Product {product_id} not in inventory")
        return {"error": "Product not found"}


# ─── Recompute Trending Products ─────────────────────────
@shared_task
def recompute_trending_products():
    """
    Recompute which products are
    selling the most.

    Scheduled to run every hour.
    Results shared with recommendation
    service via database.
    """
    from apps.orders.models import OrderItem
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Sum

    # get last 7 days
    week_ago = timezone.now() - timedelta(days=7)

    # find top selling products
    top_products = OrderItem.objects.filter(
        order__created_at__gte=week_ago,
        order__status="paid"
    ).values("product_id").annotate(
        total_sold=Sum("quantity")
    ).order_by("-total_sold")[:10]

    print(f"📊 Top products: {list(top_products)}")
    return list(top_products)
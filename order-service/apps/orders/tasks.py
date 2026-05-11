"""
Celery Tasks for Order Service
===============================
Uses email_service.py for
all email sending logic.
"""

from celery import shared_task
from .email_service import (
    send_order_confirmation,
    send_low_stock_alert,
    send_shipping_confirmation,
    send_payment_failed_email,
    send_delivery_confirmation
)


# ─── Order Confirmation ───────────────────────────────────
@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(
    self,
    order_id: str,
    user_email: str,
    total_amount: float,
    items: list
):
    """Send order confirmation in background."""
    try:
        send_order_confirmation(
            order_id=order_id,
            user_email=user_email,
            total_amount=total_amount,
            items=items
        )
        print(
            f"✅ Confirmation email sent "
            f"for order {order_id}"
        )
        return {
            "status":   "sent",
            "order_id": order_id
        }
    except Exception as exc:
        print(f"❌ Email failed: {exc}")
        raise self.retry(exc=exc, countdown=60)


# ─── Low Stock Alert ──────────────────────────────────────
@shared_task(bind=True, max_retries=3)
def send_low_stock_alert_task(
    self,
    product_id: str,
    current_quantity: int,
    vendor_email: str
):
    """Send low stock alert in background."""
    try:
        send_low_stock_alert(
            product_id=product_id,
            current_quantity=current_quantity,
            vendor_email=vendor_email
        )
        print(
            f"✅ Low stock alert sent "
            f"for {product_id}"
        )
        return {
            "status":     "sent",
            "product_id": product_id
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# ─── Shipping Confirmation ────────────────────────────────
@shared_task(bind=True, max_retries=3)
def send_shipping_confirmation_email(
    self,
    order_id: str,
    user_email: str,
    tracking_number: str = None
):
    """Send shipping update in background."""
    try:
        send_shipping_confirmation(
            order_id=order_id,
            user_email=user_email,
            tracking_number=tracking_number
        )
        print(
            f"✅ Shipping email sent "
            f"for order {order_id}"
        )
        return {
            "status":   "sent",
            "order_id": order_id
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# ─── Payment Failed ───────────────────────────────────────
@shared_task(bind=True, max_retries=3)
def send_payment_failed_notification(
    self,
    order_id: str,
    user_email: str,
    total_amount: float
):
    """Send payment failure notice in background."""
    try:
        send_payment_failed_email(
            order_id=order_id,
            user_email=user_email,
            total_amount=total_amount
        )
        print(
            f"✅ Payment failed email sent "
            f"for order {order_id}"
        )
        return {
            "status":   "sent",
            "order_id": order_id
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# ─── Delivery Confirmation ────────────────────────────────
@shared_task(bind=True, max_retries=3)
def send_delivery_confirmation_email(
    self,
    order_id: str,
    user_email: str
):
    """Send delivery confirmation in background."""
    try:
        send_delivery_confirmation(
            order_id=order_id,
            user_email=user_email
        )
        print(
            f"✅ Delivery email sent "
            f"for order {order_id}"
        )
        return {
            "status":   "sent",
            "order_id": order_id
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# ─── Daily Sales Report ───────────────────────────────────
@shared_task
def generate_daily_sales_report():
    """Generate daily sales summary."""
    from apps.orders.models import Order
    from django.utils import timezone
    from datetime import timedelta

    today     = timezone.now().date()
    yesterday = today - timedelta(days=1)

    orders = Order.objects.filter(
        created_at__date=yesterday,
        status="paid"
    )

    total_revenue = sum(
        float(o.total_amount) for o in orders
    )
    total_orders = orders.count()

    report = {
        "date":          str(yesterday),
        "total_orders":  total_orders,
        "total_revenue": total_revenue,
        "average_order": (
            total_revenue / total_orders
            if total_orders > 0 else 0
        )
    }

    print(f"📊 Daily Report: {report}")
    return report
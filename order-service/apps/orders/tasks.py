"""
Celery Tasks for Order Service
===============================
These are background tasks that run
without blocking the main API.

Each function decorated with @shared_task
runs in a separate Celery worker process.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


# ─── Order Confirmation Email ─────────────────────────────
@shared_task(bind=True, max_retries=3)
def send_order_confirmation_email(
    self,
    order_id: str,
    user_email: str,
    total_amount: float,
    items: list
):
    """
    Send order confirmation email to customer.

    This runs in background so customer
    gets immediate response from checkout.

    Retries up to 3 times if email fails.
    """
    try:
        # build email content
        items_text = "\n".join([
            f"- Product: {item['product_id']} "
            f"x{item['quantity']}"
            for item in items
        ])

        message = f"""
Dear Customer,

Your order has been placed successfully!

Order Details:
─────────────────
Order ID:     {order_id}
Total Amount: ${total_amount}

Items Ordered:
{items_text}

─────────────────
Thank you for shopping with ShopSphere!

We will notify you when your order ships.

Best regards,
ShopSphere Team
        """

        send_mail(
            subject=f"Order Confirmed - #{order_id[:8]}",
            message=message,
            from_email="orders@shopsphere.com",
            recipient_list=[user_email],
            fail_silently=False
        )

        print(
            f"✅ Confirmation email sent "
            f"for order {order_id}"
        )
        return {
            "status":   "sent",
            "order_id": order_id,
            "email":    user_email
        }

    except Exception as exc:
        print(f"❌ Email failed: {exc}")
        # retry after 60 seconds
        raise self.retry(exc=exc, countdown=60)


# ─── Low Stock Alert ──────────────────────────────────────
@shared_task(bind=True, max_retries=3)
def send_low_stock_alert(
    self,
    product_id: str,
    current_quantity: int,
    vendor_email: str
):
    """
    Send alert to vendor when product
    stock falls below 10.

    Triggered automatically after
    each order reduces inventory.
    """
    try:
        message = f"""
Dear Vendor,

⚠️ LOW STOCK ALERT

Your product needs restocking:

Product ID:       {product_id}
Current Stock:    {current_quantity} items remaining
Recommended:      Restock to at least 50 items

Please restock soon to avoid
missing future sales.

─────────────────────────────
ShopSphere Inventory System
        """

        send_mail(
            subject=(
                f"⚠️ Low Stock Alert - "
                f"Product {product_id[:8]}"
            ),
            message=message,
            from_email="inventory@shopsphere.com",
            recipient_list=[vendor_email],
            fail_silently=False
        )

        print(
            f"✅ Low stock alert sent "
            f"for product {product_id}"
        )
        return {
            "status":     "sent",
            "product_id": product_id,
            "quantity":   current_quantity
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# ─── Order Status Update Email ────────────────────────────
@shared_task(bind=True, max_retries=3)
def send_order_status_update(
    self,
    order_id: str,
    user_email: str,
    new_status: str
):
    """
    Send email when order status changes.
    e.g. pending → shipped → delivered
    """
    status_messages = {
        "paid":      "Your payment was confirmed!",
        "shipped":   "Your order is on the way!",
        "delivered": "Your order has been delivered!",
        "cancelled": "Your order has been cancelled."
    }

    message_text = status_messages.get(
        new_status,
        f"Your order status: {new_status}"
    )

    try:
        send_mail(
            subject=(
                f"Order Update - "
                f"#{order_id[:8]}"
            ),
            message=f"""
Dear Customer,

{message_text}

Order ID: {order_id}
Status:   {new_status.upper()}

Thank you for shopping with ShopSphere!
            """,
            from_email="orders@shopsphere.com",
            recipient_list=[user_email],
            fail_silently=False
        )

        return {
            "status":     "sent",
            "order_id":   order_id,
            "new_status": new_status
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# ─── Generate Daily Sales Report ──────────────────────────
@shared_task
def generate_daily_sales_report():
    """
    Generate daily sales summary.
    Scheduled to run every day at midnight.

    This is a periodic task —
    runs automatically on schedule.
    """
    from apps.orders.models import Order
    from django.utils import timezone
    from datetime import timedelta

    # get today's orders
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    orders = Order.objects.filter(
        created_at__date=yesterday,
        status="paid"
    )

    total_revenue = sum(
        float(o.total_amount)
        for o in orders
    )
    total_orders = orders.count()

    report = {
        "date":          str(yesterday),
        "total_orders":  total_orders,
        "total_revenue": total_revenue,
        "average_order": (
            total_revenue / total_orders
            if total_orders > 0
            else 0
        )
    }

    print(f"📊 Daily Report: {report}")
    return report
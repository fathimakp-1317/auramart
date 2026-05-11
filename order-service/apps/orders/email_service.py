"""
Email Service
=============
Handles all email sending for
the order service.

Uses Django templates for
professional looking emails.
"""

from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime


def send_order_confirmation(
    order_id: str,
    user_email: str,
    total_amount: float,
    items: list,
    order_date: str = None
):
    """
    Send order confirmation email
    to customer after successful checkout.
    """
    if not order_date:
        order_date = datetime.now().strftime(
            "%B %d, %Y at %I:%M %p"
        )

    # build items list text
    items_list = "\n".join([
        f"  • Product: {item['product_id']}"
        f"  x{item['quantity']}"
        for item in items
    ])

    # build email body
    body = f"""
Dear Customer,

Thank you for your order! 🎉

─────────────────────────────────
ORDER CONFIRMATION
─────────────────────────────────
Order ID:     {order_id}
Date:         {order_date}
Total Amount: ${total_amount}
Status:       CONFIRMED
─────────────────────────────────

ITEMS ORDERED:
{items_list}

─────────────────────────────────
WHAT HAPPENS NEXT?
─────────────────────────────────
1. We are processing your order
2. You will receive a shipping
   confirmation soon
3. Track your order at:
   {settings.FRONTEND_URL}/orders/{order_id}

─────────────────────────────────
Need help? Contact us at:
support@shopsphere.com
─────────────────────────────────

Thank you for shopping with ShopSphere!

Best regards,
The ShopSphere Team
    """

    send_mail(
        subject=f"✅ Order Confirmed #{order_id[:8]}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False
    )

    return True


def send_low_stock_alert(
    product_id: str,
    current_quantity: int,
    vendor_email: str
):
    """
    Send low stock alert to vendor
    when product stock falls below 10.
    """
    body = f"""
Dear Vendor,

⚠️  LOW STOCK ALERT

─────────────────────────────────
PRODUCT NEEDS RESTOCKING
─────────────────────────────────
Product ID:    {product_id}
Current Stock: {current_quantity} items
Alert Level:   Below 10 units
─────────────────────────────────

ACTION REQUIRED:
Please restock this product soon
to avoid missing sales.

Recommended stock level: 50+ units

Restock your product at:
{settings.FRONTEND_URL}/vendor/inventory

─────────────────────────────────
ShopSphere Inventory System
support@shopsphere.com
─────────────────────────────────
    """

    send_mail(
        subject=(
            f"⚠️ Low Stock Alert - "
            f"Product {product_id[:8]}"
        ),
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor_email],
        fail_silently=False
    )

    return True


def send_shipping_confirmation(
    order_id: str,
    user_email: str,
    tracking_number: str = None
):
    """
    Send shipping confirmation
    when order status changes to shipped.
    """
    tracking_text = (
        f"Tracking Number: {tracking_number}"
        if tracking_number
        else "Tracking info coming soon"
    )

    body = f"""
Dear Customer,

Great news! Your order is on its way! 🚚

─────────────────────────────────
SHIPPING CONFIRMATION
─────────────────────────────────
Order ID:      {order_id}
Status:        SHIPPED
{tracking_text}
Estimated:     3-5 business days
─────────────────────────────────

Track your order:
{settings.FRONTEND_URL}/orders/{order_id}

─────────────────────────────────
ShopSphere Team
support@shopsphere.com
─────────────────────────────────
    """

    send_mail(
        subject=f"🚚 Order Shipped #{order_id[:8]}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False
    )

    return True


def send_payment_failed_email(
    order_id: str,
    user_email: str,
    total_amount: float
):
    """
    Send payment failed notification
    so customer can retry.
    """
    body = f"""
Dear Customer,

Unfortunately your payment failed. ❌

─────────────────────────────────
PAYMENT FAILED
─────────────────────────────────
Order ID: {order_id}
Amount:   ${total_amount}
Status:   PAYMENT FAILED
─────────────────────────────────

WHAT TO DO:
1. Check your card details
2. Try a different payment method
3. Contact your bank if issue persists

Try again at:
{settings.FRONTEND_URL}/orders/{order_id}/pay

─────────────────────────────────
Need help? Contact us at:
support@shopsphere.com
─────────────────────────────────
    """

    send_mail(
        subject=f"❌ Payment Failed #{order_id[:8]}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False
    )

    return True


def send_delivery_confirmation(
    order_id: str,
    user_email: str
):
    """
    Send delivery confirmation
    when order is marked as delivered.
    """
    body = f"""
Dear Customer,

Your order has been delivered! 📦

─────────────────────────────────
DELIVERY CONFIRMATION
─────────────────────────────────
Order ID: {order_id}
Status:   DELIVERED
─────────────────────────────────

We hope you love your purchase!

Please leave a review at:
{settings.FRONTEND_URL}/orders/{order_id}/review

─────────────────────────────────
Thank you for shopping with
ShopSphere! 🛒

Best regards,
The ShopSphere Team
─────────────────────────────────
    """

    send_mail(
        subject=f"📦 Order Delivered #{order_id[:8]}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False
    )

    return True
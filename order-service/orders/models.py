from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING",   "Pending"),
        ("PAID",      "Paid"),
        ("SHIPPED",   "Shipped"),
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
    ]

    user_id    = models.CharField(max_length=255)
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total      = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} — {self.user_id} — {self.status}"


class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.CharField(max_length=255)
    vendor_id  = models.CharField(max_length=255)
    quantity   = models.IntegerField()
    price      = models.FloatField()

    class Meta:
        db_table = "order_items"

    def subtotal(self):
        return round(self.price * self.quantity, 2)

    def __str__(self):
        return f"Item {self.product_id} x{self.quantity} in Order #{self.order_id}"


class Payment(models.Model):
    """
    Payment record — created when customer pays for an order.
    Matches the Payment entity in the ER diagram.
    Stores payment method, status, and amount for audit trail.
    """
    STATUS_CHOICES = [
        ("PENDING",   "Pending"),
        ("SUCCESS",   "Success"),
        ("FAILED",    "Failed"),
        ("REFUNDED",  "Refunded"),
    ]

    METHOD_CHOICES = [
        ("CARD",   "Card"),
        ("UPI",    "UPI"),
        ("WALLET", "Wallet"),
        ("COD",    "Cash on Delivery"),
    ]

    order          = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    amount         = models.FloatField()
    currency       = models.CharField(max_length=10, default="INR")
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    method         = models.CharField(max_length=20, choices=METHOD_CHOICES, default="CARD")
    # Stripe fields — populated when real Stripe is wired
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_charge_id         = models.CharField(max_length=255, blank=True, null=True)
    paid_at        = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"

    def __str__(self):
        return f"Payment #{self.id} — Order #{self.order_id} — {self.status}"

# Create your models here.
import uuid
from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending",   "Pending"),
        ("paid",      "Paid"),
        ("shipped",   "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    id                = models.UUIDField(
                            primary_key=True,
                            default=uuid.uuid4,
                            editable=False)
    user_id           = models.UUIDField()
    # user_id comes from JWT token — never from request body
    status            = models.CharField(
                            max_length=20,
                            choices=STATUS_CHOICES,
                            default="pending")
    total_amount      = models.DecimalField(
                            max_digits=10,
                            decimal_places=2)
    stripe_payment_id = models.CharField(
                            max_length=255,
                            blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table  = "orders"
        ordering  = ["-created_at"]

    def __str__(self):
        return f"Order {self.id} - {self.status}"


class OrderItem(models.Model):
    id         = models.UUIDField(
                     primary_key=True,
                     default=uuid.uuid4,
                     editable=False)
    order      = models.ForeignKey(
                     Order,
                     on_delete=models.CASCADE,
                     related_name="items")
    product_id = models.UUIDField()
    # product_id from product-service — no FK across services
    vendor_id  = models.UUIDField()
    quantity   = models.IntegerField()
    unit_price = models.DecimalField(
                     max_digits=10,
                     decimal_places=2)
    # unit_price is a snapshot at time of purchase
    # even if product price changes later, this stays the same

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"Item {self.product_id} x{self.quantity}"
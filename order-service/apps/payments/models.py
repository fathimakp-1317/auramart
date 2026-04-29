import uuid
from django.db import models

class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending",  "Pending"),
        ("success",  "Success"),
        ("failed",   "Failed"),
        ("refunded", "Refunded"),
    ]

    id               = models.UUIDField(
                           primary_key=True,
                           default=uuid.uuid4,
                           editable=False)
    order            = models.ForeignKey(
                           "orders.Order",
                           on_delete=models.CASCADE,
                           related_name="payments")
    stripe_charge_id = models.CharField(
                           max_length=255,
                           blank=True)
    amount           = models.DecimalField(
                           max_digits=10,
                           decimal_places=2)
    status           = models.CharField(
                           max_length=20,
                           choices=STATUS_CHOICES,
                           default="pending")
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
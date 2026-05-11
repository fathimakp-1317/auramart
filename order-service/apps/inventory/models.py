import uuid
from django.db import models

class Inventory(models.Model):
    id           = models.UUIDField(
                       primary_key=True,
                       default=uuid.uuid4,
                       editable=False)
    product_id   = models.UUIDField(unique=True)
    quantity     = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    version      = models.IntegerField(default=0)
    # ⚠️ version column is CRITICAL
    # this is how we prevent race conditions 
    # when 2 people buy the last item at the same time
    # only the one with the correct version wins
    # every update increases version by 1

    class Meta:
        db_table = "inventory"

    def __str__(self):
        return f"Product {self.product_id} - qty:{self.quantity}"
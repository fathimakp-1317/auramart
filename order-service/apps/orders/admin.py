from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ["id", "user_id", "status",
                     "total_amount", "created_at"]
    list_filter   = ["status"]
    search_fields = ["id", "user_id"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["id", "order", "product_id",
                    "quantity", "unit_price"]
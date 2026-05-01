from django.contrib import admin
from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = [
        "product_id",
        "quantity",
        "version",
        "last_updated"
    ]
    search_fields = ["product_id"]
    list_filter   = ["last_updated"]
    ordering      = ["quantity"]
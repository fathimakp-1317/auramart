from django.urls import path
from . import views

urlpatterns = [

    # POST   /api/v1/inventory/add/
    path("add/",
         views.add_inventory,
         name="add-inventory"),

    # GET    /api/v1/inventory/all/
    path("all/",
         views.get_all_inventory,
         name="all-inventory"),

    # GET    /api/v1/inventory/low-stock/
    path("low-stock/",
         views.get_low_stock,
         name="low-stock"),

    # GET    /api/v1/inventory/{product_id}/
    path("<str:product_id>/",
         views.get_inventory,
         name="get-inventory"),

    # GET    /api/v1/inventory/{product_id}/check/
    path("<str:product_id>/check/",
         views.check_stock,
         name="check-stock"),

    # PATCH  /api/v1/inventory/{product_id}/restock/
    path("<str:product_id>/restock/",
         views.restock_inventory,
         name="restock-inventory"),

    # PATCH  /api/v1/inventory/{product_id}/reduce/
    path("<str:product_id>/reduce/",
         views.reduce_inventory,
         name="reduce-inventory"),
]
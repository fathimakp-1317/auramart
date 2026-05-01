from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({
        "success": True,
        "data": {
            "service": "order-service",
            "status":  "running",
            "port":    5003,
            "endpoints": [
                "/api/v1/cart/",
                "/api/v1/orders/",
                "/api/v1/inventory/",
            ]
        }
    })


urlpatterns = [
    path("admin/",
         admin.site.urls),
    path("health/",
         health_check,
         name="health-check"),
    path("api/v1/cart/",
         include("apps.cart.urls")),
    path("api/v1/orders/",
         include("apps.orders.urls")),
    path("api/v1/inventory/",
         include("apps.inventory.urls")),
]
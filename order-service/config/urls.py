from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({
        "success": True,
        "data": {
            "service": "order-service",
            "version": "2.0",
            "status":  "running",
            "port":    5003,
            "endpoints": {
                "cart": [
                    "GET    /api/v1/cart/{user_id}/",
                    "POST   /api/v1/cart/{user_id}/add/",
                    "PATCH  /api/v1/cart/{user_id}/update/{product_id}/",
                    "DELETE /api/v1/cart/{user_id}/remove/{product_id}/",
                    "DELETE /api/v1/cart/{user_id}/clear/",
                ],
                "orders": [
                    "POST  /api/v1/orders/place/",
                    "POST  /api/v1/orders/checkout/",
                    "GET   /api/v1/orders/all/",
                    "GET   /api/v1/orders/user/{user_id}/",
                    "GET   /api/v1/orders/{order_id}/",
                    "PATCH /api/v1/orders/{order_id}/status/",
                    "PATCH /api/v1/orders/{order_id}/cancel/",
                ],
                "inventory": [
                    "POST  /api/v1/inventory/add/",
                    "GET   /api/v1/inventory/all/",
                    "GET   /api/v1/inventory/low-stock/",
                    "GET   /api/v1/inventory/{product_id}/",
                    "GET   /api/v1/inventory/{product_id}/check/",
                    "PATCH /api/v1/inventory/{product_id}/restock/",
                    "PATCH /api/v1/inventory/{product_id}/reduce/",
                ],
                "payments": [
                    "POST /api/v1/payments/{order_id}/initiate/",
                    "POST /api/v1/payments/{order_id}/verify/",
                    "GET  /api/v1/payments/{order_id}/status/",
                    "POST /api/v1/payments/{order_id}/refund/",
                    "POST /api/v1/payments/webhook/",
                ]
            }
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
    path("api/v1/payments/",
         include("apps.payments.urls")),
]
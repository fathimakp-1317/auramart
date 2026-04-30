from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({
        "success": True,
        "data": {
            "service": "order-service",
            "status":  "running",
            "port":    5003
        }
    })


urlpatterns = [
    path("admin/",       admin.site.urls),
    path("health/",      health_check,
                         name="health-check"),
    path("api/v1/cart/", include("apps.cart.urls")),
]
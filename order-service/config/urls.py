import os
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.conf.urls.static import static


def health_check(request):
    return JsonResponse({
        "success": True,
        "data": {
            "service": "order-service",
            "status":  "running",
            "port":    5003
        }
    })


def serve_frontend(request, page):
    """Serve frontend HTML pages."""
    file_path = os.path.join(
        settings.BASE_DIR,
        "frontend",
        "pages",
        f"{page}.html"
    )

    if os.path.exists(file_path):
        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:
            return HttpResponse(
                f.read(),
                content_type=(
                    "text/html; charset=utf-8"
                )
            )

    from django.http import Http404
    raise Http404(f"Page {page} not found")


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

    # frontend pages
    path("pages/cart/",
         serve_frontend,
         {"page": "cart"},
         name="cart-page"),
    path("pages/checkout/",
         serve_frontend,
         {"page": "checkout"},
         name="checkout-page"),
    path("pages/orders/",
         serve_frontend,
         {"page": "orders"},
         name="orders-page"),

] + static(
    settings.STATIC_URL,
    document_root=os.path.join(
        settings.BASE_DIR,
        "frontend"
    )
)
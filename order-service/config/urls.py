from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Cart endpoints
    path("api/v1/cart/",
         include("apps.cart.urls")),
]
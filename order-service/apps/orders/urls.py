from django.urls import path
from . import views

urlpatterns = [

    # POST   /api/v1/orders/checkout/
    path("checkout/",
         views.checkout,
         name="checkout"),

    # POST   /api/v1/orders/create/
    path("create/",
         views.create_order,
         name="create-order"),

    # GET    /api/v1/orders/all/
    path("all/",
         views.get_all_orders,
         name="all-orders"),

    # GET    /api/v1/orders/user/{user_id}/
    path("user/<str:user_id>/",
         views.get_user_orders,
         name="user-orders"),

    # GET    /api/v1/orders/{order_id}/
    path("<str:order_id>/",
         views.get_order,
         name="get-order"),

    # PATCH  /api/v1/orders/{order_id}/status/
    path("<str:order_id>/status/",
         views.update_order_status,
         name="update-order-status"),

    # PATCH  /api/v1/orders/{order_id}/cancel/
    path("<str:order_id>/cancel/",
         views.cancel_order,
         name="cancel-order"),
]
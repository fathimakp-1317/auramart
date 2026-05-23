from django.urls import path
from . import views

urlpatterns = [
    path("hello",                          views.hello,          name="hello"),
    path("orders",                         views.orders_list,    name="orders"),        # GET=list, POST=create
    path("orders/<int:order_id>",          views.order_detail,   name="order_detail"),
    path("orders/<int:order_id>/pay",      views.pay_order,      name="pay_order"),
    path("vendor/orders",                  views.vendor_orders,  name="vendor_orders"),
    path("orders/<int:order_id>/status", views.update_order_status, name="update_status"),
    path("orders/<int:order_id>/cancel", views.cancel_order, name="cancel_order"),
]

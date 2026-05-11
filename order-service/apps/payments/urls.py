from django.urls import path
from . import views

urlpatterns = [

    # POST /api/v1/payments/{order_id}/initiate/
    path("<str:order_id>/initiate/",
         views.initiate_payment,
         name="initiate-payment"),

    # POST /api/v1/payments/{order_id}/verify/
    path("<str:order_id>/verify/",
         views.verify_payment,
         name="verify-payment"),

    # GET  /api/v1/payments/{order_id}/status/
    path("<str:order_id>/status/",
         views.get_payment_status,
         name="payment-status"),

    # POST /api/v1/payments/{order_id}/refund/
    path("<str:order_id>/refund/",
         views.refund_payment,
         name="refund-payment"),

    # POST /api/v1/payments/webhook/
    path("webhook/",
         views.stripe_webhook,
         name="stripe-webhook"),
]
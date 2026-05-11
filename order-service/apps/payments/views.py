import stripe
import json
import os
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from apps.orders.models import Order
from .models import Payment
from .stripe_client import (
    create_payment_intent,
    confirm_payment_intent,
    create_refund
)


# ─── Create Payment Intent ────────────────────────────────
@api_view(["POST"])
def initiate_payment(request, order_id):
    """
    Create a Stripe payment intent for an order.

    Frontend calls this first to get client_secret.
    Then frontend uses client_secret to show
    Stripe payment form to customer.

    Returns client_secret that frontend needs.
    """
    order = get_object_or_404(Order, id=order_id)

    # dont allow payment for cancelled orders
    if order.status == "cancelled":
        return Response({
            "success": False,
            "error": {
                "code":    "ORDER_CANCELLED",
                "message": "Cannot pay for a cancelled order"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    # dont allow double payment
    if order.status == "paid":
        return Response({
            "success": False,
            "error": {
                "code":    "ALREADY_PAID",
                "message": "This order is already paid"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # create payment intent in Stripe
        payment_data = create_payment_intent(
            amount=float(order.total_amount),
            order_id=str(order.id)
        )

        # save payment record in our database
        Payment.objects.create(
            order=order,
            stripe_charge_id=payment_data["payment_intent_id"],
            amount=order.total_amount,
            status="pending"
        )

        return Response({
            "success": True,
            "data": {
                "order_id":          str(order.id),
                "total_amount":      float(order.total_amount),
                "payment_intent_id": payment_data["payment_intent_id"],
                "client_secret":     payment_data["client_secret"],
                # ← send this to frontend
                "currency":          "usd"
            }
        })

    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code":    "STRIPE_ERROR",
                "message": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Verify Payment ───────────────────────────────────────
@api_view(["POST"])
def verify_payment(request, order_id):
    """
    Verify a payment after frontend confirms it.

    Frontend calls this after customer enters card.
    We check with Stripe if payment succeeded.

    Expects:
    { "payment_intent_id": "pi_xxx" }
    """
    order = get_object_or_404(Order, id=order_id)

    payment_intent_id = request.data.get(
        "payment_intent_id"
    )

    if not payment_intent_id:
        return Response({
            "success": False,
            "error": {
                "code":    "MISSING_FIELD",
                "message": "payment_intent_id is required"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # check payment status with Stripe
        payment_data = confirm_payment_intent(
            payment_intent_id
        )

        payment = get_object_or_404(
            Payment,
            stripe_charge_id=payment_intent_id
        )

        if payment_data["status"] == "succeeded":
            # update payment record
            payment.status = "success"
            payment.save()

            # update order status to paid
            order.status            = "paid"
            order.stripe_payment_id = payment_intent_id
            order.save()

            return Response({
                "success": True,
                "data": {
                    "order_id":     str(order.id),
                    "order_status": order.status,
                    "payment":      payment_data
                }
            })
        else:
            payment.status = "failed"
            payment.save()

            return Response({
                "success": False,
                "error": {
                    "code":    "PAYMENT_FAILED",
                    "message": f"Payment status: "
                               f"{payment_data['status']}"
                }
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code":    "STRIPE_ERROR",
                "message": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Get Payment Status ───────────────────────────────────
@api_view(["GET"])
def get_payment_status(request, order_id):
    """
    Get current payment status for an order.
    """
    order   = get_object_or_404(Order, id=order_id)
    payment = Payment.objects.filter(
        order=order
    ).last()

    if not payment:
        return Response({
            "success": False,
            "error": {
                "code":    "NO_PAYMENT",
                "message": "No payment found for this order"
            }
        }, status=status.HTTP_404_NOT_FOUND)

    return Response({
        "success": True,
        "data": {
            "order_id":          str(order.id),
            "order_status":      order.status,
            "payment_status":    payment.status,
            "amount":            float(payment.amount),
            "stripe_charge_id":  payment.stripe_charge_id,
            "created_at":        payment.created_at
        }
    })


# ─── Refund Payment ───────────────────────────────────────
@api_view(["POST"])
def refund_payment(request, order_id):
    """
    Refund a payment for an order.
    Only paid orders can be refunded.
    """
    order = get_object_or_404(Order, id=order_id)

    if order.status != "paid":
        return Response({
            "success": False,
            "error": {
                "code":    "NOT_PAID",
                "message": "Only paid orders can be refunded"
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    payment = Payment.objects.filter(
        order=order,
        status="success"
    ).last()

    if not payment:
        return Response({
            "success": False,
            "error": {
                "code":    "NO_PAYMENT",
                "message": "No successful payment found"
            }
        }, status=status.HTTP_404_NOT_FOUND)

    try:
        refund_data = create_refund(
            payment_intent_id=payment.stripe_charge_id
        )

        # update records
        payment.status = "refunded"
        payment.save()

        order.status = "cancelled"
        order.save()

        return Response({
            "success": True,
            "data": {
                "order_id":    str(order.id),
                "refund_id":   refund_data["refund_id"],
                "amount":      refund_data["amount"],
                "status":      refund_data["status"]
            }
        })

    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code":    "REFUND_FAILED",
                "message": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Stripe Webhook ───────────────────────────────────────
@csrf_exempt
def stripe_webhook(request):
    """
    Stripe calls this URL automatically
    after every payment event.

    This is how Stripe tells us:
    - payment succeeded
    - payment failed
    - refund processed
    etc.
    """
    payload    = request.body
    sig_header = request.META.get(
        "HTTP_STRIPE_SIGNATURE"
    )
    webhook_secret = os.getenv(
        "STRIPE_WEBHOOK_SECRET", ""
    )

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # handle payment success
    if event["type"] == "payment_intent.succeeded":
        intent   = event["data"]["object"]
        order_id = intent["metadata"].get("order_id")

        if order_id:
            try:
                order        = Order.objects.get(id=order_id)
                order.status = "paid"
                order.stripe_payment_id = intent["id"]
                order.save()

                Payment.objects.filter(
                    stripe_charge_id=intent["id"]
                ).update(status="success")

                print(f"Order {order_id} marked as paid")
            except Order.DoesNotExist:
                print(f"Order {order_id} not found")

    # handle payment failure
    elif event["type"] == "payment_intent.payment_failed":
        intent   = event["data"]["object"]
        order_id = intent["metadata"].get("order_id")

        if order_id:
            Payment.objects.filter(
                stripe_charge_id=intent["id"]
            ).update(status="failed")

            print(f"Payment failed for order {order_id}")

    return HttpResponse(status=200)
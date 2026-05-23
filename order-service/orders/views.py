import json, requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pika import BasicProperties

from .models import Order, OrderItem, Payment
from .auth import verify_token
from .rabbitmq import get_channel

PRODUCT_SERVICE = settings.PRODUCT_SERVICE_URL


def order_to_dict(order, include_items=False):
    data = {
        "order_id":   order.id,
        "status":     order.status,
        "total":      float(order.total),
        "created_at": str(order.created_at),
        "updated_at": str(order.updated_at),
    }
    if include_items:
        data["items"] = [
            {
                "product_id": i.product_id,
                "vendor_id":  i.vendor_id,
                "quantity":   i.quantity,
                "price":      float(i.price),
                "subtotal":   i.subtotal(),
            }
            for i in order.items.all()
        ]
    return data


@api_view(["GET"])
def hello(request):
    return Response({"message": "Order Service running (Django + DRF)"})


@api_view(["GET", "POST"])
def orders_list(request):
    user, err = verify_token(request)
    if err:
        return err

    if request.method == "GET":
        orders = Order.objects.filter(user_id=user["sub"]).order_by("-created_at")
        return Response([order_to_dict(o) for o in orders])

    raw_items = request.data.get("items", [])
    if not raw_items:
        return Response({"error": "Order must contain at least one item"}, status=400)

    enriched = []
    for item in raw_items:
        pid = str(item.get("product_id", "")).strip()
        qty = int(item.get("quantity", 1))
        if not pid:
            return Response({"error": "product_id required for each item"}, status=400)
        if qty < 1:
            return Response({"error": f"Invalid quantity for {pid}"}, status=400)
        try:
            resp = requests.get(f"{PRODUCT_SERVICE}/products/{pid}", timeout=5)
        except requests.exceptions.ConnectionError:
            return Response({"error": "Product service unavailable"}, status=502)
        if resp.status_code == 404:
            return Response({"error": f"Product {pid} not found"}, status=404)
        if resp.status_code != 200:
            return Response({"error": "Product service error"}, status=502)
        product = resp.json()
        if product.get("stock", 0) < qty:
            return Response({
                "detail": (
                    f"Insufficient stock for '{product['name']}'. "
                    f"Requested: {qty}, Available: {product['stock']}"
                )
            }, status=400)
        enriched.append({
            "product_id": pid,
            "vendor_id":  product["vendor_id"],
            "quantity":   qty,
            "price":      float(product["price"]),
            "name":       product["name"],
        })

    total = round(sum(i["price"] * i["quantity"] for i in enriched), 2)
    order = Order.objects.create(user_id=user["sub"], total=total)
    for item in enriched:
        OrderItem.objects.create(
            order=order,
            product_id=item["product_id"],
            vendor_id=item["vendor_id"],
            quantity=item["quantity"],
            price=item["price"],
        )

    for item in enriched:
        try:
            requests.patch(
                f"{PRODUCT_SERVICE}/products/{item['product_id']}/stock",
                json={"quantity": item["quantity"]},
                timeout=5,
            )
        except Exception as e:
            print(f"[order] Stock decrement failed for {item['product_id']}: {e}")

    try:
        ch = get_channel()
        if ch:
            ch.basic_publish(
                exchange="",
                routing_key="order_created",
                body=json.dumps({
                    "order_id": order.id,
                    "user_id":  user["sub"],
                    "email":    user.get("email", ""),
                    "items":    enriched,
                    "total":    total,
                }),
                properties=BasicProperties(delivery_mode=2),
            )
    except Exception as e:
        print(f"[order] RabbitMQ publish failed: {e}")

    return Response({
        "order_id": order.id,
        "total":    total,
        "status":   "PENDING",
        "items":    len(enriched),
    }, status=201)


@api_view(["GET"])
def order_detail(request, order_id):
    user, err = verify_token(request)
    if err:
        return err

    role = user.get("role")

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    # Customers can only see their own orders
    if role == "customer" and str(order.user_id) != str(user["sub"]):
        return Response({"error": "Order not found"}, status=404)

    # Vendors can only see orders containing their products
    if role == "vendor":
        vendor_items = OrderItem.objects.filter(order_id=order_id, vendor_id=user["sub"])
        if not vendor_items.exists():
            return Response({"error": "No items from your store in this order"}, status=404)
        return Response({
            "order_id":   order.id,
            "status":     order.status,
            "total":      float(order.total),
            "created_at": str(order.created_at),
            "updated_at": str(order.updated_at),
            "items": [
                {
                    "product_id": i.product_id,
                    "vendor_id":  i.vendor_id,
                    "quantity":   i.quantity,
                    "price":      float(i.price),
                    "subtotal":   i.subtotal(),
                }
                for i in vendor_items
            ]
        })

    return Response(order_to_dict(order, include_items=True))


@api_view(["POST"])
def pay_order(request, order_id):
    user, err = verify_token(request)
    if err:
        return err
    try:
        order = Order.objects.get(id=order_id, user_id=user["sub"])
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)
    if order.status == "PAID":
        return Response({"error": "Order already paid"}, status=400)

    # ── Stripe (uncomment when ready) ─────────────────────────────────────────
    # import stripe
    # stripe.api_key = settings.STRIPE_SECRET_KEY
    # try:
    #     intent = stripe.PaymentIntent.create(
    #         amount=int(order.total * 100),
    #         currency="inr",
    #         payment_method=request.data.get("stripe_token"),
    #         confirm=True,
    #     )
    #     stripe_id = intent.id
    # except stripe.error.CardError as e:
    #     return Response({"error": str(e.user_message)}, status=402)
    # ─────────────────────────────────────────────────────────────────────────

    from django.utils import timezone as tz

    # Update order status
    order.status = "PAID"
    order.save()

    # Create Payment record (matches ER diagram)
    Payment.objects.update_or_create(
        order=order,
        defaults={
            "amount":   order.total,
            "currency": "INR",
            "status":   "SUCCESS",
            "method":   request.data.get("method", "CARD"),
            "paid_at":  tz.now(),
        }
    )

    return Response({
        "message":  "Payment successful",
        "order_id": order.id,
        "status":   "PAID"
    })


@api_view(["PATCH"])
def update_order_status(request, order_id):
    user, err = verify_token(request)
    if err:
        return err

    if user.get("role") not in ("vendor", "admin"):
        return Response({"error": "Only vendors or admins can update order status"}, status=403)

    valid_statuses = ["PENDING", "PAID", "SHIPPED", "DELIVERED"]
    new_status = request.data.get("status", "").upper()

    if new_status not in valid_statuses:
        return Response({"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}, status=400)

    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    if user.get("role") == "vendor":
        if not OrderItem.objects.filter(order_id=order_id, vendor_id=user["sub"]).exists():
            return Response({"error": "You don't have items in this order"}, status=403)

    status_rank = {s: i for i, s in enumerate(valid_statuses)}
    if status_rank[new_status] <= status_rank[order.status]:
        return Response({"error": f"Cannot change status from {order.status} to {new_status}"}, status=400)

    order.status = new_status
    order.save()
    return Response({"order_id": order.id, "status": new_status, "message": f"Order status updated to {new_status}"})


@api_view(["GET"])
def vendor_orders(request):
    user, err = verify_token(request)
    if err:
        return err
    if user.get("role") != "vendor":
        return Response({"error": "Only vendors can access this"}, status=403)
    items = OrderItem.objects.filter(vendor_id=user["sub"])

    # Fetch product names from product-service
    product_names = {}
    unique_pids = list(set(i.product_id for i in items))
    for pid in unique_pids:
        try:
            resp = requests.get(f"{PRODUCT_SERVICE}/products/{pid}", timeout=3)
            if resp.status_code == 200:
                product_names[pid] = resp.json().get("name", "")
        except Exception:
            pass

    return Response([
        {
            "order_id":     i.order_id,
            "product_id":   i.product_id,
            "product_name": product_names.get(i.product_id, ""),
            "quantity":     i.quantity,
            "price":        float(i.price),
            "subtotal":     i.subtotal(),
        }
        for i in items
    ])

@api_view(["POST"])
def cancel_order(request, order_id):
    """
    Customer can cancel a PENDING order.
    Stock is restored for each item on cancellation.
    """
    user, err = verify_token(request)
    if err:
        return err

    try:
        order = Order.objects.get(id=order_id, user_id=user["sub"])
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=404)

    if order.status != "PENDING":
        return Response(
            {"error": f"Cannot cancel a {order.status} order. Only orders that haven't shipped can be cancelled."},
            status=400
        )

    # Restore stock for each item
    items = OrderItem.objects.filter(order_id=order_id)
    for item in items:
        try:
            requests.patch(
                f"{PRODUCT_SERVICE}/products/{item.product_id}/stock",
                json={"quantity": -item.quantity},  # negative = restore
                timeout=5
            )
        except Exception as e:
            print(f"[cancel] Stock restore failed for {item.product_id}: {e}")

    order.status = "CANCELLED"
    order.save()

    # Publish cancellation event for notification-service
    try:
        ch = get_channel()
        if ch:
            ch.basic_publish(
                exchange="",
                routing_key="order_cancelled",
                body=json.dumps({
                    "order_id": order.id,
                    "user_id":  user["sub"],
                    "email":    user.get("email", ""),
                    "total":    float(order.total),
                }),
                properties=BasicProperties(delivery_mode=2),
            )
    except Exception as e:
        print(f"[cancel] RabbitMQ publish failed: {e}")

    return Response({
        "message":  f"Order #{order_id} has been cancelled",
        "order_id": order.id,
        "status":   "CANCELLED"
    })
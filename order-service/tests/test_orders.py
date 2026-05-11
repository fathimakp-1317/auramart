"""
Order Tests
===========
Tests for order management endpoints.
"""

import json
import pytest
from django.test import TestCase, Client
from apps.orders.models import Order, OrderItem
from apps.inventory.models import Inventory
from apps.cart.redis_cart import (
    add_to_cart, clear_cart
)
from tests.factories import (
    OrderFactory,
    OrderItemFactory,
    InventoryFactory
)


class OrderModelTest(TestCase):
    """Tests for Order model."""

    def test_create_order(self):
        """Order is created with correct fields."""
        order = OrderFactory(
            user_id="model-test-user",
            total_amount=99.99,
            status="pending"
        )

        self.assertIsNotNone(order.id)
        self.assertEqual(
            order.user_id, "model-test-user"
        )
        self.assertEqual(order.status, "pending")

    def test_order_default_status_is_pending(self):
        """New order status defaults to pending."""
        order = OrderFactory()
        self.assertEqual(order.status, "pending")

    def test_order_str_representation(self):
        """Order string shows id and status."""
        order = OrderFactory(status="paid")
        self.assertIn("paid", str(order))

    def test_create_order_with_items(self):
        """Order can have multiple items."""
        order = OrderFactory()
        item1 = OrderItemFactory(order=order)
        item2 = OrderItemFactory(order=order)

        self.assertEqual(
            order.items.count(), 2
        )


class OrderAPITest(TestCase):
    """Tests for Order API endpoints."""

    def setUp(self):
        self.client = Client()

    def test_create_order_endpoint(self):
        """POST /api/v1/orders/create/ works."""
        response = self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({
                "user_id": "api-user-001",
                "items": [{
                    "product_id": "prod-001",
                    "vendor_id":  "vendor-001",
                    "quantity":   2,
                    "unit_price": 29.99
                }]
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("id", data["data"])

    def test_create_order_missing_items(self):
        """Creating order without items returns 400."""
        response = self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({
                "user_id": "api-user-001",
                "items":   []
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_get_user_orders(self):
        """GET /api/v1/orders/user/{id}/ returns orders."""
        # create some orders first
        OrderFactory(user_id="get-test-user")
        OrderFactory(user_id="get-test-user")
        OrderFactory(user_id="other-user")

        response = self.client.get(
            "/api/v1/orders/user/get-test-user/"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        # should only return 2 orders
        # not the one from other-user
        self.assertEqual(
            data["data"]["count"], 2
        )

    def test_get_single_order(self):
        """GET /api/v1/orders/{id}/ returns order."""
        order = OrderFactory()
        response = self.client.get(
            f"/api/v1/orders/{order.id}/"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(
            data["data"]["id"], str(order.id)
        )

    def test_get_nonexistent_order(self):
        """Getting nonexistent order returns 404."""
        import uuid
        response = self.client.get(
            f"/api/v1/orders/{uuid.uuid4()}/"
        )
        self.assertEqual(response.status_code, 404)

    def test_update_order_status(self):
        """PATCH status endpoint works."""
        order = OrderFactory(status="pending")
        response = self.client.patch(
            f"/api/v1/orders/{order.id}/status/",
            data=json.dumps({"status": "shipped"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["data"]["new_status"], "shipped"
        )

    def test_update_order_invalid_status(self):
        """Invalid status returns 400."""
        order = OrderFactory()
        response = self.client.patch(
            f"/api/v1/orders/{order.id}/status/",
            data=json.dumps(
                {"status": "invalid-status"}
            ),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_cancel_pending_order(self):
        """Cancelling pending order works."""
        order = OrderFactory(status="pending")
        response = self.client.patch(
            f"/api/v1/orders/{order.id}/cancel/"
        )
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, "cancelled")

    def test_cancel_shipped_order_fails(self):
        """Cannot cancel already shipped order."""
        order = OrderFactory(status="shipped")
        response = self.client.patch(
            f"/api/v1/orders/{order.id}/cancel/"
        )
        self.assertEqual(response.status_code, 400)


class CheckoutTest(TestCase):
    """Tests for checkout flow."""

    def setUp(self):
        self.client  = Client()
        self.user_id = "checkout-test-user"

        # create inventory
        self.inventory = InventoryFactory(
            product_id="checkout-prod-001",
            quantity=10
        )

        # add to cart
        add_to_cart(
            user_id=self.user_id,
            product_id="checkout-prod-001",
            quantity=2,
            price=49.99
        )

    def tearDown(self):
        clear_cart(self.user_id)

    def test_checkout_success(self):
        """Checkout with valid cart succeeds."""
        response = self.client.post(
            "/api/v1/orders/checkout/",
            data=json.dumps(
                {"user_id": self.user_id}
            ),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("order_id", data["data"])

    def test_checkout_reduces_inventory(self):
        """Checkout reduces inventory correctly."""
        self.client.post(
            "/api/v1/orders/checkout/",
            data=json.dumps(
                {"user_id": self.user_id}
            ),
            content_type="application/json"
        )

        self.inventory.refresh_from_db()
        # started with 10, bought 2
        self.assertEqual(
            self.inventory.quantity, 8
        )

    def test_checkout_clears_cart(self):
        """Cart is empty after successful checkout."""
        self.client.post(
            "/api/v1/orders/checkout/",
            data=json.dumps(
                {"user_id": self.user_id}
            ),
            content_type="application/json"
        )

        from apps.cart.redis_cart import get_cart
        cart = get_cart(self.user_id)
        self.assertEqual(cart["items"], [])

    def test_checkout_empty_cart_fails(self):
        """Checkout with empty cart returns 400."""
        clear_cart(self.user_id)
        response = self.client.post(
            "/api/v1/orders/checkout/",
            data=json.dumps(
                {"user_id": self.user_id}
            ),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_checkout_insufficient_stock_fails(self):
        """Checkout fails if not enough stock."""
        # set inventory to 1
        self.inventory.quantity = 1
        self.inventory.save()

        # try to buy 5
        clear_cart(self.user_id)
        add_to_cart(
            user_id=self.user_id,
            product_id="checkout-prod-001",
            quantity=5,
            price=49.99
        )

        response = self.client.post(
            "/api/v1/orders/checkout/",
            data=json.dumps(
                {"user_id": self.user_id}
            ),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    # ... inside class CheckoutTest or OrderAPITest ...

    def test_get_all_orders(self):
        """GET /api/v1/orders/all/ returns all orders."""
        OrderFactory()
        OrderFactory()
        OrderFactory()

        response = self.client.get("/api/v1/orders/all/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(data["data"]["count"], 3)

    def test_create_order_without_user_id(self):
        """Creating order without user_id returns 400."""
        response = self.client.post(
            "/api/v1/orders/create/",
            data=json.dumps({
                "items": [{
                    "product_id": "prod-001",
                    "vendor_id":  "vendor-001",
                    "quantity":   1,
                    "unit_price": 10.00
                }]
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_place_order_without_user_id(self):
        """Place order without user_id returns 400."""
        # Note: Ensure /place/ exists in urls.py, otherwise change to /create/ or /checkout/
        response = self.client.post(
            "/api/v1/orders/place/",
            data=json.dumps({}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
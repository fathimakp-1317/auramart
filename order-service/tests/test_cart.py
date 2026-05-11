"""
Cart Tests
==========
Tests for Redis cart functionality.
"""

import pytest
from django.test import TestCase, Client
from apps.cart.redis_cart import (
    get_cart,
    add_to_cart,
    remove_from_cart,
    update_quantity,
    clear_cart
)


class CartRedisTest(TestCase):
    """Tests for Redis cart operations."""

    def setUp(self):
        """Set up test data."""
        self.user_id    = "test-user-cart-001"
        self.product_id = "test-product-001"
        # clear cart before each test
        clear_cart(self.user_id)

    def tearDown(self):
        """Clean up after each test."""
        clear_cart(self.user_id)

    # ── Get Cart Tests ────────────────────────────────────

    def test_get_empty_cart(self):
        """Empty cart returns empty items list."""
        cart = get_cart(self.user_id)
        self.assertEqual(cart["items"], [])
        self.assertEqual(cart["total"], 0)

    def test_get_cart_returns_correct_user(self):
        """Cart returns correct user_id."""
        cart = get_cart(self.user_id)
        self.assertEqual(
            cart["user_id"],
            self.user_id
        )

    # ── Add to Cart Tests ─────────────────────────────────

    def test_add_item_to_cart(self):
        """Adding item to cart works."""
        cart = add_to_cart(
            user_id=self.user_id,
            product_id=self.product_id,
            quantity=2,
            price=29.99
        )

        self.assertEqual(len(cart["items"]), 1)
        self.assertEqual(
            cart["items"][0]["product_id"],
            self.product_id
        )
        self.assertEqual(
            cart["items"][0]["quantity"], 2
        )
        self.assertEqual(
            cart["items"][0]["price"], 29.99
        )

    def test_add_same_item_increases_quantity(self):
        """Adding same item increases quantity."""
        add_to_cart(
            self.user_id,
            self.product_id,
            2,
            29.99
        )
        cart = add_to_cart(
            self.user_id,
            self.product_id,
            3,
            29.99
        )

        self.assertEqual(len(cart["items"]), 1)
        self.assertEqual(
            cart["items"][0]["quantity"], 5
        )

    def test_add_multiple_different_items(self):
        """Adding different items creates multiple entries."""
        add_to_cart(
            self.user_id, "product-1", 1, 10.00
        )
        cart = add_to_cart(
            self.user_id, "product-2", 2, 20.00
        )

        self.assertEqual(len(cart["items"]), 2)

    def test_cart_total_calculated_correctly(self):
        """Cart total is sum of all items."""
        add_to_cart(
            self.user_id, "product-1", 2, 10.00
        )
        cart = add_to_cart(
            self.user_id, "product-2", 1, 30.00
        )

        # 2 x 10.00 + 1 x 30.00 = 50.00
        self.assertEqual(cart["total"], 50.00)

    # ── Remove from Cart Tests ────────────────────────────

    def test_remove_item_from_cart(self):
        """Removing item from cart works."""
        add_to_cart(
            self.user_id,
            self.product_id,
            2,
            29.99
        )
        cart = remove_from_cart(
            self.user_id,
            self.product_id
        )

        self.assertEqual(len(cart["items"]), 0)

    def test_remove_nonexistent_item(self):
        """Removing item not in cart doesnt crash."""
        cart = remove_from_cart(
            self.user_id,
            "nonexistent-product"
        )
        self.assertEqual(cart["items"], [])

    # ── Update Quantity Tests ─────────────────────────────

    def test_update_quantity(self):
        """Updating quantity works."""
        add_to_cart(
            self.user_id,
            self.product_id,
            2,
            29.99
        )
        cart = update_quantity(
            self.user_id,
            self.product_id,
            5
        )

        self.assertEqual(
            cart["items"][0]["quantity"], 5
        )

    def test_update_quantity_to_zero_removes_item(self):
        """Setting quantity to 0 removes the item."""
        add_to_cart(
            self.user_id,
            self.product_id,
            2,
            29.99
        )
        cart = update_quantity(
            self.user_id,
            self.product_id,
            0
        )

        self.assertEqual(len(cart["items"]), 0)

    # ── Clear Cart Tests ──────────────────────────────────

    def test_clear_cart(self):
        """Clearing cart removes all items."""
        add_to_cart(
            self.user_id, "product-1", 1, 10.00
        )
        add_to_cart(
            self.user_id, "product-2", 2, 20.00
        )
        clear_cart(self.user_id)

        cart = get_cart(self.user_id)
        self.assertEqual(cart["items"], [])


class CartAPITest(TestCase):
    """Tests for Cart API endpoints."""

    def setUp(self):
        self.client  = Client()
        self.user_id = "api-test-user-001"
        clear_cart(self.user_id)

    def tearDown(self):
        clear_cart(self.user_id)

    def test_get_cart_endpoint(self):
        """GET /api/v1/cart/{user_id}/ returns 200."""
        response = self.client.get(
            f"/api/v1/cart/{self.user_id}/"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])

    def test_add_item_endpoint(self):
        """POST /api/v1/cart/{user_id}/add/ works."""
        import json
        response = self.client.post(
            f"/api/v1/cart/{self.user_id}/add/",
            data=json.dumps({
                "product_id": "api-prod-001",
                "quantity":   2,
                "price":      49.99
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(
            len(data["data"]["items"]), 1
        )

    def test_add_item_missing_product_id(self):
        """Adding item without product_id returns 400."""
        import json
        response = self.client.post(
            f"/api/v1/cart/{self.user_id}/add/",
            data=json.dumps({
                "quantity": 1,
                "price":    10.00
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_clear_cart_endpoint(self):
        """DELETE /api/v1/cart/{user_id}/clear/ works."""
        import json
        # add item first
        self.client.post(
            f"/api/v1/cart/{self.user_id}/add/",
            data=json.dumps({
                "product_id": "test-prod",
                "quantity":   1,
                "price":      10.00
            }),
            content_type="application/json"
        )

        # clear cart
        response = self.client.delete(
            f"/api/v1/cart/{self.user_id}/clear/"
        )
        self.assertEqual(response.status_code, 200)

        # verify empty
        cart_response = self.client.get(
            f"/api/v1/cart/{self.user_id}/"
        )
        cart_data = cart_response.json()
        self.assertEqual(
            len(cart_data["data"]["items"]), 0
        )
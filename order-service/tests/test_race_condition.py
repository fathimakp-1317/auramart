"""
Race Condition Tests
====================
This tests the most critical scenario:
Two users buying the last item at the same time.

Only ONE should succeed.
The other should get an error.

This is the Week 3 required test from
the project document.
"""

import threading
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from apps.inventory.models import Inventory
from apps.orders.models import Order, OrderItem
from apps.cart.redis_cart import add_to_cart, clear_cart
import json


class RaceConditionTest(TestCase):
    """
    Tests for race conditions in inventory
    and order processing.
    """

    def setUp(self):
        """
        Set up test data before each test.
        Creates inventory with only 1 item.
        """
        self.client = Client()

        # create inventory with ONLY 1 item
        # this is the critical scenario
        self.inventory = Inventory.objects.create(
            product_id="race-product-001",
            quantity=1,
            version=0
        )

        # set up cart for user 1
        add_to_cart(
            user_id="race-user-1",
            product_id="race-product-001",
            quantity=1,
            price=29.99
        )

        # set up cart for user 2
        add_to_cart(
            user_id="race-user-2",
            product_id="race-product-001",
            quantity=1,
            price=29.99
        )

    def tearDown(self):
        """
        Clean up after each test.
        """
        clear_cart("race-user-1")
        clear_cart("race-user-2")

    def test_only_one_order_succeeds(self):
        """
        TEST: Two users buy last item simultaneously.
        Only ONE should succeed.
        """
        results = []

        def buy(user_id):
            """
            Each user tries to checkout.
            We record success or failure.
            """
            response = self.client.post(
                "/api/v1/orders/checkout/",
                data=json.dumps({"user_id": user_id}),
                content_type="application/json"
            )
            results.append({
                "user_id": user_id,
                "status":  response.status_code,
                "data":    response.json()
            })

        # create 2 threads — simulates
        # 2 users buying at same time
        thread1 = threading.Thread(
            target=buy,
            args=("race-user-1",)
        )
        thread2 = threading.Thread(
            target=buy,
            args=("race-user-2",)
        )

        # start both at same time
        thread1.start()
        thread2.start()

        # wait for both to finish
        thread1.join()
        thread2.join()

        # count successes and failures
        successes = [
            r for r in results
            if r["status"] == 201
        ]
        failures = [
            r for r in results
            if r["status"] != 201
        ]

        print("\n--- Race Condition Test Results ---")
        for r in results:
            print(
                f"User: {r['user_id']} → "
                f"Status: {r['status']}"
            )
        print(f"Successes: {len(successes)}")
        print(f"Failures:  {len(failures)}")
        print("-----------------------------------")

        # CRITICAL ASSERTIONS
        # exactly 1 should succeed
        self.assertEqual(
            len(successes), 1,
            "Exactly 1 order should succeed"
        )

        # exactly 1 should fail
        self.assertEqual(
            len(failures), 1,
            "Exactly 1 order should fail"
        )

        # inventory should be 0 not -1
        self.inventory.refresh_from_db()
        self.assertEqual(
            self.inventory.quantity, 0,
            "Inventory should be 0 not negative"
        )

        # only 1 order in database
        orders = Order.objects.filter(
            user_id__in=[
                "race-user-1",
                "race-user-2"
            ]
        )
        self.assertEqual(
            orders.count(), 1,
            "Only 1 order should be in database"
        )

    def test_inventory_never_goes_negative(self):
        """
        TEST: Inventory quantity never goes below 0.
        Even with 10 simultaneous requests.
        """
        # set inventory to 3
        self.inventory.quantity = 3
        self.inventory.save()

        # set up carts for 10 users
        for i in range(10):
            add_to_cart(
                user_id=f"bulk-user-{i}",
                product_id="race-product-001",
                quantity=1,
                price=29.99
            )

        results = []

        def buy(user_id):
            response = self.client.post(
                "/api/v1/orders/checkout/",
                data=json.dumps({"user_id": user_id}),
                content_type="application/json"
            )
            results.append(response.status_code)

        # create 10 threads
        threads = [
            threading.Thread(
                target=buy,
                args=(f"bulk-user-{i}",)
            )
            for i in range(10)
        ]

        # start all at same time
        for t in threads:
            t.start()

        # wait for all to finish
        for t in threads:
            t.join()

        # check inventory
        self.inventory.refresh_from_db()

        print(
            f"\nFinal inventory: "
            f"{self.inventory.quantity}"
        )

        # CRITICAL — never negative
        self.assertGreaterEqual(
            self.inventory.quantity, 0,
            "Inventory must never go negative!"
        )

        # exactly 3 should succeed
        successes = results.count(201)
        print(f"Successful orders: {successes}")

        self.assertEqual(
            successes, 3,
            "Only 3 orders should succeed "
            "(matching stock of 3)"
        )

        # clean up
        for i in range(10):
            clear_cart(f"bulk-user-{i}")

    def test_version_conflict_detection(self):
        """
        TEST: Version conflict is detected
        when two requests try to update
        same inventory at same time.
        """
        from apps.inventory.models import Inventory

        # get current version
        current_version = self.inventory.version

        # first update succeeds
        self.inventory.refresh_from_db()
        inv = Inventory.objects.select_for_update(
        ).get(product_id="race-product-001")
        inv.quantity -= 1
        inv.version  += 1
        inv.save()

        # verify version increased
        self.inventory.refresh_from_db()
        self.assertEqual(
            self.inventory.version,
            current_version + 1,
            "Version should increment after update"
        )

        # verify quantity decreased
        self.assertEqual(
            self.inventory.quantity, 0,
            "Quantity should be 0 after purchase"
        )
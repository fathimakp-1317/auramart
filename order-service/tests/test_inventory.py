"""
Inventory Tests
===============
Tests for inventory management.
"""

import json
from django.test import TestCase, Client
from apps.inventory.models import Inventory
from tests.factories import InventoryFactory


class InventoryModelTest(TestCase):
    """Tests for Inventory model."""

    def test_create_inventory(self):
        """Inventory created with correct fields."""
        inventory = InventoryFactory(
            product_id="inv-test-001",
            quantity=50,
            version=0
        )
        self.assertEqual(
            inventory.product_id, "inv-test-001"
        )
        self.assertEqual(inventory.quantity, 50)
        self.assertEqual(inventory.version, 0)

    def test_version_increments(self):
        """Version increments when quantity changes."""
        inventory = InventoryFactory(
            quantity=10,
            version=0
        )
        inventory.quantity -= 2
        inventory.version  += 1
        inventory.save()

        inventory.refresh_from_db()
        self.assertEqual(inventory.version, 1)
        self.assertEqual(inventory.quantity, 8)


class InventoryAPITest(TestCase):
    """Tests for Inventory API endpoints."""

    def setUp(self):
        self.client = Client()

    def test_add_inventory(self):
        """POST /api/v1/inventory/add/ works."""
        response = self.client.post(
            "/api/v1/inventory/add/",
            data=json.dumps({
                "product_id": "new-prod-001",
                "quantity":   100
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(
            data["data"]["quantity"], 100
        )

    def test_add_duplicate_inventory_fails(self):
        """Adding same product twice returns 400."""
        InventoryFactory(product_id="dup-prod-001")
        response = self.client.post(
            "/api/v1/inventory/add/",
            data=json.dumps({
                "product_id": "dup-prod-001",
                "quantity":   50
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_get_inventory(self):
        """GET /api/v1/inventory/{id}/ works."""
        inv = InventoryFactory(
            product_id="get-prod-001",
            quantity=25
        )
        response = self.client.get(
            f"/api/v1/inventory/{inv.product_id}/"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["data"]["quantity"], 25
        )

    def test_check_stock_available(self):
        """Stock check returns available when enough."""
        InventoryFactory(
            product_id="check-prod-001",
            quantity=20
        )
        response = self.client.get(
            "/api/v1/inventory/check-prod-001"
            "/check/?quantity=5"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(
            data["data"]["is_available"]
        )


    def test_check_stock_unavailable(self):
        """Stock check returns unavailable when low."""
        InventoryFactory(
            product_id="low-prod-001",
            quantity=2
        )
        response = self.client.get(
            "/api/v1/inventory/low-prod-001"
            "/check/?quantity=10"
        )
        data = response.json()
        self.assertFalse(
            data["data"]["is_available"]
        )

    def test_restock_inventory(self):
        """Restock increases quantity correctly."""
        inv = InventoryFactory(
            product_id="restock-prod-001",
            quantity=10
        )
        response = self.client.patch(
            f"/api/v1/inventory/"
            f"{inv.product_id}/restock/",
            data=json.dumps(
                {"quantity_to_add": 20}
            ),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            data["data"]["new_quantity"], 30
        )

    def test_low_stock_endpoint(self):
        """Low stock endpoint returns items below 10."""
        InventoryFactory(
            product_id="low-1",
            quantity=3
        )
        InventoryFactory(
            product_id="low-2",
            quantity=7
        )
        InventoryFactory(
            product_id="normal-1",
            quantity=50
        )

        response = self.client.get(
            "/api/v1/inventory/low-stock/"
        )
        data = response.json()
        # only 2 items below 10
        self.assertEqual(
            data["data"]["count"], 2
        )


    def test_reduce_inventory(self):
        """Reduce inventory endpoint works."""
        inv = InventoryFactory(
            product_id="reduce-prod-001",
            quantity=10,
            version=0
        )
        response = self.client.patch(
            f"/api/v1/inventory/{inv.product_id}/reduce/",
            data=json.dumps({
                "quantity":        3,
                "current_version": 0
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["data"]["new_quantity"], 7)

    def test_reduce_inventory_version_conflict(self):
        """Wrong version returns 409 conflict."""
        inv = InventoryFactory(
            product_id="conflict-prod-001",
            quantity=10,
            version=5
        )
        response = self.client.patch(
            f"/api/v1/inventory/{inv.product_id}/reduce/",
            data=json.dumps({
                "quantity":        1,
                "current_version": 0  # wrong version — should be 5
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)

    def test_reduce_inventory_insufficient_stock(self):
        """Reducing more than stock fails."""
        inv = InventoryFactory(
            product_id="nostock-prod-001",
            quantity=2,
            version=0
        )
        response = self.client.patch(
            f"/api/v1/inventory/{inv.product_id}/reduce/",
            data=json.dumps({
                "quantity":        10,
                "current_version": 0
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    def test_get_all_inventory(self):
        """GET /api/v1/inventory/all/ returns all."""
        InventoryFactory(product_id="all-prod-1")
        InventoryFactory(product_id="all-prod-2")

        response = self.client.get("/api/v1/inventory/all/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(data["data"]["count"], 2)    

    
"""
 Concurrency / Race Condition Test
=======================================================
Proves that simultaneous purchases of the last item in stock
do NOT oversell. Only one request should succeed; all others
should get a 400 "Insufficient stock" error.

How it works:
  1. Registers N test users
  2. Creates a test product with stock = 1
  3. Fires N purchase requests simultaneously using threads
  4. Verifies exactly 1 succeeded and N-1 failed with stock error
  5. Verifies final stock is 0 (not negative)

Usage:
  python tests/concurrency_test.py
  python tests/concurrency_test.py --users 20
  python tests/concurrency_test.py --base-url http://localhost
"""

import argparse
import threading
import requests
import uuid
import time
from datetime import datetime

BASE_URL = "http://localhost"
RESULTS  = []
LOCK     = threading.Lock()


def register_and_login(email, password):
    """Register a user and return their JWT token."""
    requests.post(f"{BASE_URL}/auth/register", json={
        "email":    email,
        "password": password,
        "role":     "customer"
    })
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email":    email,
        "password": password
    })
    return res.json().get("token")


def create_test_product(vendor_token, stock=1):
    """Create a product with exactly 1 unit in stock."""
    res = requests.post(
        f"{BASE_URL}/products/products",
        json={
            "name":        f"Test Product {uuid.uuid4().hex[:6]}",
            "description": "Concurrency test product",
            "price":       99.99,
            "stock":       stock,
        },
        headers={"Authorization": f"Bearer {vendor_token}"}
    )
    return res.json().get("id")


def attempt_purchase(user_index, token, product_id, barrier):
    """
    Each thread waits at the barrier so all fire at the same instant.
    Records whether the purchase succeeded or failed.
    """
    # All threads wait here until every thread is ready
    barrier.wait()

    start = time.time()
    try:
        # Step 1: Add to cart
        cart_res = requests.post(
            f"{BASE_URL}/cart/cart",
            json={"product_id": product_id, "quantity": 1},
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )

        if cart_res.status_code != 201:
            result = {
                "user":    user_index,
                "outcome": "FAIL",
                "reason":  f"Cart add failed: {cart_res.status_code} — {cart_res.json().get('detail', '')}",
                "ms":      round((time.time() - start) * 1000)
            }
        else:
            # Step 2: Place order
            order_res = requests.post(
                f"{BASE_URL}/orders/orders",
                json={"items": [{"product_id": product_id, "quantity": 1}]},
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )

            if order_res.status_code in (200, 201):
                result = {
                    "user":     user_index,
                    "outcome":  "SUCCESS",
                    "order_id": order_res.json().get("order_id"),
                    "ms":       round((time.time() - start) * 1000)
                }
            else:
                result = {
                    "user":    user_index,
                    "outcome": "FAIL",
                    "reason":  order_res.json().get("detail", "Unknown error"),
                    "ms":      round((time.time() - start) * 1000)
                }

    except Exception as e:
        result = {
            "user":    user_index,
            "outcome": "ERROR",
            "reason":  str(e),
            "ms":      round((time.time() - start) * 1000)
        }

    with LOCK:
        RESULTS.append(result)


def check_stock(product_id):
    """Fetch current stock from product-service."""
    res = requests.get(f"{BASE_URL}/products/products/{product_id}")
    if res.status_code == 200:
        return res.json().get("stock", -1)
    return -1


def run_test(base_url, num_users, initial_stock):
    global BASE_URL, RESULTS
    BASE_URL = base_url
    RESULTS  = []

    print("=" * 60)
    print("  ShopSphere — Concurrency / Race Condition Test")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Simultaneous users : {num_users}")
    print(f"  Product stock      : {initial_stock}")
    print(f"  Expected successes : {initial_stock}")
    print(f"  Expected failures  : {num_users - initial_stock}")
    print("=" * 60)

    # ── Step 1: Create a vendor and test product ──────────────────
    print("\n[1/4] Setting up vendor and test product...")
    vendor_email = f"vendor_{uuid.uuid4().hex[:6]}@test.com"
    vendor_pass  = "testpass123"

    requests.post(f"{BASE_URL}/auth/register", json={
        "email":    vendor_email,
        "password": vendor_pass,
        "role":     "vendor"
    })
    vendor_login = requests.post(f"{BASE_URL}/auth/login", json={
        "email": vendor_email, "password": vendor_pass
    })
    vendor_token = vendor_login.json().get("token")

    if not vendor_token:
        print("Could not create vendor. Is the stack running?")
        return

    product_id = create_test_product(vendor_token, stock=initial_stock)
    if not product_id:
        print("Could not create test product.")
        return

    print(f"  Product created: {product_id}  (stock={initial_stock})")

    # ── Step 2: Register all test users ──────────────────────────
    print(f"\n[2/4] Registering {num_users} test users...")
    tokens = []
    for i in range(num_users):
        email    = f"testuser_{uuid.uuid4().hex[:6]}@test.com"
        password = "testpass123"
        token    = register_and_login(email, password)
        if token:
            tokens.append(token)
        print(f"   User {i+1}/{num_users} ready", end="\r")
    print(f"  {len(tokens)} users registered")

    # ── Step 3: Fire all purchase attempts simultaneously ─────────
    print(f"\n[3/4] Firing {len(tokens)} simultaneous purchase requests...")
    print("   All threads waiting at barrier — will fire at the same instant...")

    barrier = threading.Barrier(len(tokens))
    threads = []

    for i, token in enumerate(tokens):
        t = threading.Thread(
            target=attempt_purchase,
            args=(i + 1, token, product_id, barrier)
        )
        threads.append(t)

    # Start all threads
    for t in threads:
        t.start()

    # Wait for all to finish
    for t in threads:
        t.join()

    print(f" All requests completed")

    # ── Step 4: Analyse results ───────────────────────────────────
    print(f"\n[4/4] Results:\n")

    successes = [r for r in RESULTS if r["outcome"] == "SUCCESS"]
    failures  = [r for r in RESULTS if r["outcome"] == "FAIL"]
    errors    = [r for r in RESULTS if r["outcome"] == "ERROR"]

    # Print each result
    for r in sorted(RESULTS, key=lambda x: x["user"]):
        if r["outcome"] == "SUCCESS":
            print(f"   User {r['user']:>2}  ✅ SUCCESS  order_id={r.get('order_id')}  ({r['ms']}ms)")
        elif r["outcome"] == "FAIL":
            print(f"   User {r['user']:>2}  ❌ FAIL     {r.get('reason', '')}  ({r['ms']}ms)")
        else:
            print(f"   User {r['user']:>2}  ⚠️  ERROR    {r.get('reason', '')}  ({r['ms']}ms)")

    # Check final stock
    final_stock = check_stock(product_id)

    print(f"\n{'=' * 60}")
    print(f"  SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Successful purchases : {len(successes)}  (expected {initial_stock})")
    print(f"  Rejected (no stock)  : {len(failures)}")
    print(f"  Errors               : {len(errors)}")
    print(f"  Final stock          : {final_stock}  (expected 0)")
    print(f"{'=' * 60}")

    # ── Verdict ───────────────────────────────────────────────────
    correct_successes = len(successes) == initial_stock
    correct_stock     = final_stock == 0
    no_oversell       = final_stock >= 0

    print()
    if correct_successes and correct_stock:
        print("  TEST PASSED")
        print("  Race condition handled correctly.")
        print("  Stock integrity maintained under concurrent load.")
    elif not no_oversell:
        print("  TEST FAILED — OVERSELL DETECTED")
        print(f"  Stock went negative ({final_stock}). Data integrity compromised.")
    elif len(successes) > initial_stock:
        print("   TEST FAILED — OVERSELL DETECTED")
        print(f"  {len(successes)} orders succeeded but only {initial_stock} units existed.")
    else:
        print("   PARTIAL — check results above")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--users",         type=int, default=10,                  help="Number of simultaneous users (default: 10)")
    parser.add_argument("--stock",         type=int, default=1,                   help="Initial product stock (default: 1)")
    parser.add_argument("--base-url",      type=str, default="http://localhost",  help="Base URL of the stack")
    args = parser.parse_args()

    run_test(args.base_url, args.users, args.stock)
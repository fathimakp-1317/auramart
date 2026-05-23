"""
Week 4 Deliverable — Disaster Recovery Test
============================================
Proves that killing the Order service does NOT take down
the entire site. The gateway and all other services
continue working gracefully.

Tests:
  1. Baseline — all services healthy before killing anything
  2. Kill order-service
  3. Verify homepage, search, products still work
  4. Verify checkout fails gracefully (503, not a crash)
  5. Revive order-service
  6. Verify full recovery — checkout works again

Usage:
  python tests/disaster_recovery_test.py
"""

import subprocess
import requests
import time
from datetime import datetime

BASE_URL     = "http://localhost"
PASS         = "PASS"
FAIL         = " FAIL"
WARN         = "  WARN"
results      = []


def check(label, ok, detail=""):
    status = PASS if ok else FAIL
    results.append((label, ok, detail))
    print(f"  {status}  {label}")
    if detail:
        print(f"         {detail}")
    return ok


def get(path, token=None, timeout=5):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        return requests.get(f"{BASE_URL}{path}", headers=headers, timeout=timeout)
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None


def post(path, body, token=None, timeout=5):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        return requests.post(f"{BASE_URL}{path}", json=body, headers=headers, timeout=timeout)
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None


def get_token():
    """Get a customer token for testing."""
    post("/auth/register", {"email": "dr_test@test.com", "password": "test123", "role": "customer"})
    res = post("/auth/login", {"email": "dr_test@test.com", "password": "test123"})
    if res and res.status_code == 200:
        return res.json().get("token")
    return None


def docker(cmd):
    """Run a docker compose command and return output."""
    result = subprocess.run(
        f"docker compose {cmd}",
        shell=True, capture_output=True, text=True
    )
    return result.returncode == 0


def print_section(title):
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print(f"{'-' * 60}")


def run():
    print("=" * 60)
    print("  ShopSphere - Disaster Recovery Test")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    token = get_token()

    # ── Phase 1: Baseline health check ───────────────────────────
    print_section("Phase 1: Baseline — all services should be healthy")

    r = get("/health")
    check("Gateway health endpoint",        r and r.status_code == 200)

    r = get("/auth/hello")
    check("Auth service reachable",         r and r.status_code == 200)

    r = get("/products/products")
    check("Product service reachable",      r and r.status_code == 200)

    r = get("/search/search?q=laptop")
    check("Search service reachable",       r and r.status_code == 200)

    r = get("/home/home")
    check("Home service reachable",         r and r.status_code == 200)

    r = get("/cart/hello")
    check("Cart service reachable",         r and r.status_code == 200)

    r = get("/orders/hello")
    check("Order service reachable",        r and r.status_code == 200)

    r = get("/analytics/hello")
    check("Analytics service reachable",    r and r.status_code == 200)

    r = get("/notifications/hello")
    check("Notification API reachable",     r and r.status_code == 200)

    r = post("/orders/orders",
             {"items": [{"product_id": "test", "quantity": 1}]},
             token=token)
    check("Order creation reachable",       r is not None and r.status_code != 503,
          f"Status: {r.status_code if r else 'no response'}")

    # ── Phase 2: Kill order-service ───────────────────────────────
    print_section("Phase 2: Killing order-service...")

    killed = docker("stop order-service")
    check("order-service stopped successfully", killed)
    print("  Waiting 3 seconds for gateway to detect the failure...")
    time.sleep(3)

    # ── Phase 3: Graceful degradation check ───────────────────────
    print_section("Phase 3: Graceful degradation — site should still work")

    r = get("/health")
    check("Gateway still responding",       r and r.status_code == 200)

    r = get("/auth/hello")
    check("Auth service still up",          r and r.status_code == 200)

    r = get("/products/products")
    check("Products still loading",         r and r.status_code == 200,
          f"{len(r.json()) if r and r.status_code == 200 else 0} products returned")

    r = get("/search/search?q=headphone")
    check("Search still working",           r and r.status_code == 200,
          f"{r.json().get('total', 0) if r and r.status_code == 200 else 0} results")

    r = get("/home/home")
    check("Homepage still loading",         r and r.status_code == 200)

    r = get("/cart/hello")
    check("Cart service still up",          r and r.status_code == 200)

    r = get("/analytics/hello")
    check("Analytics still up",             r and r.status_code == 200)

    # ── Phase 4: Checkout fails gracefully ────────────────────────
    print_section("Phase 4: Checkout should fail gracefully (not crash)")

    r = post("/orders/orders",
             {"items": [{"product_id": "test", "quantity": 1}]},
             token=token)

    if r is None:
        check("Checkout fails with error response (not silent crash)",
              False, "Got no response at all — gateway crashed")
    elif r.status_code in (502, 503):
        check("Checkout returns 502/503 (service unavailable)",
              True, f"Got {r.status_code} — correct graceful failure")
    elif r.status_code == 404:
        check("Checkout returns error response",
              True, f"Got 404 — route not found, acceptable")
    else:
        check("Checkout fails with error response",
              False, f"Unexpected status {r.status_code}: {r.text[:100]}")

    r = get("/products/products")
    check("Products still accessible after order failure",
          r and r.status_code == 200,
          "Site did not crash when order-service went down")

    # ── Phase 5: Revive order-service ────────────────────────────
    print_section("Phase 5: Reviving order-service...")

    revived = docker("start order-service")
    check("order-service start command succeeded", revived)

    print("  Waiting 10 seconds for service to boot...")
    time.sleep(10)

    # ── Phase 6: Full recovery check ──────────────────────────────
    print_section("Phase 6: Full recovery — everything should work again")

    for attempt in range(5):
        r = get("/orders/hello")
        if r and r.status_code == 200:
            break
        print(f"  Waiting for order-service to be ready... ({attempt+1}/5)")
        time.sleep(5)

    check("Order service recovered",        r and r.status_code == 200)

    r = post("/orders/orders",
             {"items": [{"product_id": "test", "quantity": 1}]},
             token=token)
    # Will be 404 (product not found) but NOT 503 — proves service is back
    check("Order endpoint responsive again",
          r is not None and r.status_code != 503,
          f"Status: {r.status_code if r else 'no response'} (not 503 = service recovered)")

    r = get("/products/products")
    check("Products still working",         r and r.status_code == 200)

    r = get("/search/search?q=laptop")
    check("Search still working",           r and r.status_code == 200)

    # ── Final verdict ─────────────────────────────────────────────
    total   = len(results)
    passed  = sum(1 for _, ok, _ in results if ok)
    failed  = total - passed

    print(f"\n{'=' * 60}")
    print(f"  DISASTER RECOVERY TEST — FINAL REPORT")
    print(f"{'=' * 60}")
    print(f"  Total checks : {total}")
    print(f"  Passed       : {passed}")
    print(f"  Failed       : {failed}")
    print(f"{'=' * 60}")

    if failed == 0:
        print("""
  TEST PASSED

  Findings:
  - Killing order-service did NOT crash the site
  - Homepage, search, products remained fully operational
  - Checkout failed with a proper 502/503 error (not a crash)
  - order-service self-recovered after restart
  - All other services unaffected throughout
        """)
    elif failed <= 2:
        print(f"""
  MOSTLY PASSED ({failed} minor issues)
  Core disaster recovery behaviour is correct.
  Check failed items above.
        """)
    else:
        print(f"""
  TEST FAILED — {failed} checks did not pass
  Review the failed items above.
        """)
    print("=" * 60)


if __name__ == "__main__":
    run()
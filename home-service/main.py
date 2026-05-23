"""
Home Service — aggregates data for the homepage.

Returns:
  - recommended: full product objects for this user (via recommendation-service)
  - trending:    full product objects for trending products (via analytics-service)
  - latest:      5 most recent products
"""
import requests, json, redis
from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI(title="ShopSphere Home Service")
app.add_middleware(GZipMiddleware, minimum_size=1000)

r = redis.Redis(host="redis", port=6379, decode_responses=True)

PRODUCT_SERVICE        = "http://product-service:8000"
RECOMMENDATION_SERVICE = "http://recommendation-service:8000"
ANALYTICS_SERVICE      = "http://analytics-service:8000"


def safe_get(url, headers=None, timeout=3):
    """HTTP GET that never raises — returns None on any failure."""
    try:
        resp = requests.get(url, headers=headers or {}, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"[home] Request failed {url}: {e}")
    return None


@app.get("/hello")
def hello():
    return {"message": "Home Service running"}


@app.get("/home")
def home(request: Request):
    auth = request.headers.get("Authorization")
    headers = {"Authorization": auth} if auth else {}

    # ── All products (cached by product-service) ──────────────────────────
    all_products_raw = safe_get(f"{PRODUCT_SERVICE}/products")
    all_products     = all_products_raw or []
    products_by_id   = {str(p["id"]): p for p in all_products}

    # ── Latest 5 products ─────────────────────────────────────────────────
    latest = all_products[-5:] if all_products else []

    # ── Trending (from analytics-service, graceful fallback) ──────────────
    trending_raw = safe_get(f"{ANALYTICS_SERVICE}/trending")
    trending = []
    if trending_raw:
        for t in trending_raw:
            pid = str(t.get("product_id", ""))
            if pid in products_by_id:
                trending.append(products_by_id[pid])

    # ── Personalised recommendations (only if logged in) ──────────────────
    recommended = []
    if auth:
        rec_resp = safe_get(
            f"{RECOMMENDATION_SERVICE}/recommend",
            headers=headers
        )
        if rec_resp and "recommendations" in rec_resp:
            for pid in rec_resp["recommendations"]:
                if str(pid) in products_by_id:
                    recommended.append(products_by_id[str(pid)])

    return {
        "recommended": recommended[:8],   # cap at 8 for UI
        "trending":    trending[:8],
        "latest":      latest,
    }

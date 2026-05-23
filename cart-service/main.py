"""
Cart Service — Redis-backed shopping cart.

Cart is stored in Redis as a hash keyed by product_id:
    cart:{user_id}  →  { product_id: quantity, ... }

Using a hash (not a list) means:
  - No duplicate entries — adding same product merges quantities
  - O(1) remove by product_id — no index shifting
  - O(1) update quantity — no full rewrite
  - Clean PATCH /cart/{product_id} for qty changes

Fixes from original:
  - Remove by index → remove by product_id (reliable, index-independent)
  - Duplicate append → merge/increment quantity
  - No PATCH endpoint → added (frontend Cart.jsx calls it)
  - No stock check before add → validates stock with product-service
  - Checkout clears cart even on order failure → only clears on success
  - auth.py hardcoded secret, no Bearer check → fixed (from Module 1)
  - requirements had sqlalchemy/psycopg2/pika (unused) → removed
"""
import json, os, requests
import redis
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from auth import verify_token

app = FastAPI(title="ShopSphere Cart Service")
app.add_middleware(GZipMiddleware, minimum_size=1000)

r = redis.Redis(host="redis", port=6379, decode_responses=True)

PRODUCT_SERVICE = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8000")
ORDER_SERVICE   = os.getenv("ORDER_SERVICE_URL",   "http://order-service:8000")


# ── Helpers ───────────────────────────────────────────────────────────────────
def cart_key(user_id: str) -> str:
    return f"cart:{user_id}"

def get_cart(user_id: str) -> dict:
    """Returns {product_id: quantity} dict from Redis hash."""
    raw = r.hgetall(cart_key(user_id))
    return {pid: int(qty) for pid, qty in raw.items()}

def fetch_product(product_id: str) -> dict:
    """Fetch product details from product-service. Raises 404/502 on failure."""
    try:
        resp = requests.get(f"{PRODUCT_SERVICE}/products/{product_id}", timeout=5)
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Product service unavailable")
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Product service error")
    return resp.json()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/hello")
def hello():
    return {"message": "Cart Service running"}


@app.get("/cart")
def view_cart(user=Depends(verify_token)):
    """
    Returns cart items as a list with full product details resolved.
    Each item: { product_id, name, price, stock, quantity, subtotal }
    """
    cart = get_cart(user["sub"])
    if not cart:
        return []

    items = []
    for pid, qty in cart.items():
        try:
            product = fetch_product(pid)
            items.append({
                "product_id": pid,
                "name":       product["name"],
                "price":      product["price"],
                "stock":      product["stock"],
                "quantity":   qty,
                "subtotal":   round(product["price"] * qty, 2),
            })
        except HTTPException:
            # Product was deleted after being added to cart — skip it
            r.hdel(cart_key(user["sub"]), pid)

    return items


@app.post("/cart", status_code=201)
def add_to_cart(data: dict, user=Depends(verify_token)):
    """
    Add a product to cart or increment its quantity if already present.
    Validates stock before adding.
    """
    product_id = str(data.get("product_id", "")).strip()
    quantity   = int(data.get("quantity", 1))

    if not product_id:
        raise HTTPException(status_code=400, detail="product_id is required")
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    # Validate product exists and has enough stock
    product = fetch_product(product_id)

    # How much is already in cart?
    key         = cart_key(user["sub"])
    current_qty = int(r.hget(key, product_id) or 0)
    new_qty     = current_qty + quantity

    if product["stock"] < new_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product['stock']} units available. "
                   f"You already have {current_qty} in your cart."
        )

    r.hset(key, product_id, new_qty)

    return {
        "message":    "Added to cart",
        "product_id": product_id,
        "quantity":   new_qty,
    }


@app.patch("/cart/{product_id}")
def update_quantity(product_id: str, data: dict, user=Depends(verify_token)):
    """
    Update the quantity of a specific product in the cart.
    If quantity is set to 0 or below, the item is removed.
    """
    quantity = int(data.get("quantity", 1))
    key      = cart_key(user["sub"])

    if not r.hexists(key, product_id):
        raise HTTPException(status_code=404, detail="Item not in cart")

    if quantity <= 0:
        r.hdel(key, product_id)
        return {"message": "Item removed from cart"}

    # Validate stock for the new quantity
    product = fetch_product(product_id)
    if product["stock"] < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Only {product['stock']} units available"
        )

    r.hset(key, product_id, quantity)
    return {
        "message":    "Quantity updated",
        "product_id": product_id,
        "quantity":   quantity,
    }


@app.delete("/cart/{product_id}")
def remove_item(product_id: str, user=Depends(verify_token)):
    """Remove a specific product from cart by product_id (not by index)."""
    key = cart_key(user["sub"])

    if not r.hexists(key, product_id):
        raise HTTPException(status_code=404, detail="Item not in cart")

    r.hdel(key, product_id)
    return {"message": "Item removed from cart"}


@app.delete("/cart")
def clear_cart(user=Depends(verify_token)):
    """Remove all items from the cart."""
    r.delete(cart_key(user["sub"]))
    return {"message": "Cart cleared"}


@app.post("/checkout")
def checkout(request: Request, user=Depends(verify_token)):
    """
    One-click checkout: forwards cart items to order-service,
    then clears the cart ONLY if the order was created successfully.
    """
    cart = get_cart(user["sub"])
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    items = [
        {"product_id": pid, "quantity": qty}
        for pid, qty in cart.items()
    ]

    # Forward to order-service
    try:
        resp = requests.post(
            f"{ORDER_SERVICE}/orders",
            json={"items": items},
            headers={"Authorization": request.headers.get("Authorization", "")},
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=502, detail="Order service unavailable")

    if resp.status_code not in (200, 201):
        # Order failed — do NOT clear cart
        detail = resp.json().get("detail") or resp.json().get("error") or "Order failed"
        raise HTTPException(status_code=resp.status_code, detail=detail)

    # Only clear cart on successful order
    r.delete(cart_key(user["sub"]))
    return resp.json()

import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Connect to Redis ─────────────────────────────────────
r = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379")
)

# Cart stays alive for 7 days
CART_TTL = 7 * 24 * 60 * 60  # in seconds


# ─── Get Cart ─────────────────────────────────────────────
def get_cart(user_id: str) -> dict:
    """
    Get the current cart for a user.
    Returns empty cart if user has no cart yet.
    """
    data = r.get(f"cart:{user_id}")
    if data:
        return json.loads(data)
    return {"user_id": user_id, "items": [], "total": 0}


# ─── Add Item to Cart ─────────────────────────────────────
def add_to_cart(user_id: str,
                product_id: str,
                quantity: int,
                price: float) -> dict:
    """
    Add a product to the cart.
    If product already exists, increase the quantity.
    """
    cart = get_cart(user_id)

    # check if product already in cart
    for item in cart["items"]:
        if item["product_id"] == product_id:
            # product exists — just increase quantity
            item["quantity"] += quantity
            item["subtotal"] = round(
                item["quantity"] * item["price"], 2
            )
            _save_cart(user_id, cart)
            return cart

    # product not in cart — add it fresh
    cart["items"].append({
        "product_id": product_id,
        "quantity":   quantity,
        "price":      price,
        "subtotal":   round(quantity * price, 2)
    })

    # recalculate total
    _update_total(cart)
    _save_cart(user_id, cart)
    return cart


# ─── Remove Item from Cart ────────────────────────────────
def remove_from_cart(user_id: str,
                     product_id: str) -> dict:
    """
    Remove a specific product from the cart completely.
    """
    cart = get_cart(user_id)

    cart["items"] = [
        item for item in cart["items"]
        if item["product_id"] != product_id
    ]

    _update_total(cart)
    _save_cart(user_id, cart)
    return cart


# ─── Update Item Quantity ─────────────────────────────────
def update_quantity(user_id: str,
                    product_id: str,
                    quantity: int) -> dict:
    """
    Change the quantity of a specific product in the cart.
    If quantity is 0, remove the item completely.
    """
    if quantity == 0:
        return remove_from_cart(user_id, product_id)

    cart = get_cart(user_id)

    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] = quantity
            item["subtotal"] = round(quantity * item["price"], 2)

    _update_total(cart)
    _save_cart(user_id, cart)
    return cart


# ─── Clear Cart ───────────────────────────────────────────
def clear_cart(user_id: str):
    """
    Empty the cart completely.
    Called after a successful order is placed.
    """
    r.delete(f"cart:{user_id}")


# ─── Helper: Save Cart to Redis ───────────────────────────
def _save_cart(user_id: str, cart: dict):
    """
    Save cart to Redis with 7 day expiry.
    Private function — only used inside this file.
    """
    r.setex(
        f"cart:{user_id}",  # key
        CART_TTL,            # expiry in seconds
        json.dumps(cart)     # value
    )


# ─── Helper: Recalculate Total ────────────────────────────
def _update_total(cart: dict):
    """
    Recalculate the cart total price.
    Private function — only used inside this file.
    """
    cart["total"] = round(
        sum(item["subtotal"] for item in cart["items"]), 2
    )
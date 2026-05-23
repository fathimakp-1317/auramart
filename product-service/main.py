import json, os, time
import pika, redis, requests
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from elasticsearch import Elasticsearch
from auth import verify_token
from database import engine, SessionLocal, Base
from models import Product, Category, Review
from rate_limiter import rate_limit

ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")

app = FastAPI(title="ShopSphere Product Service")
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ── Startup: wait for Postgres, then create tables ───────────────────────────
time.sleep(5)
Base.metadata.create_all(bind=engine)

# ── Redis ─────────────────────────────────────────────────────────────────────
r = redis.Redis(host="redis", port=6379, decode_responses=True)

# ── Elasticsearch ─────────────────────────────────────────────────────────────
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = Elasticsearch(ES_URL)

ES_INDEX = "products"
ES_MAPPING = {
    "mappings": {
        "properties": {
            "name":        {"type": "text",    "analyzer": "standard"},
            "description": {"type": "text",    "analyzer": "standard"},
            "price":       {"type": "float"},
            "stock":       {"type": "integer"},
            "vendor_id":   {"type": "keyword"},
            "category_id": {"type": "keyword"},
            "avg_rating":  {"type": "float"},
            "review_count":{"type": "integer"},
        }
    }
}

# ── RabbitMQ — retry on cold start ────────────────────────────────────────────
_rmq_conn = None
_rmq_ch   = None

def get_channel():
    global _rmq_conn, _rmq_ch
    try:
        if _rmq_conn and _rmq_conn.is_open:
            return _rmq_ch
    except Exception:
        pass
    for _ in range(10):
        try:
            _rmq_conn = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
            _rmq_ch   = _rmq_conn.channel()
            _rmq_ch.queue_declare(queue="product_view", durable=True)
            return _rmq_ch
        except Exception:
            time.sleep(3)
    return None


# ── Helpers ───────────────────────────────────────────────────────────────────
def product_dict(p: Product) -> dict:
    return {
        "id":           p.id,
        "name":         p.name,
        "description":  p.description,
        "price":        p.price,
        "vendor_id":    p.vendor_id,
        "category_id":  p.category_id,
        "stock":        p.stock,
        "avg_rating":   round(p.avg_rating or 0.0, 1),
        "review_count": p.review_count or 0,
        "images":       json.loads(p.images or "[]"),
    }

def es_index(p: Product):
    """Index or update a product document in Elasticsearch."""
    try:
        es.index(index=ES_INDEX, id=str(p.id), document=product_dict(p))
    except Exception as e:
        print(f"[ES] index error: {e}")

def es_delete(product_id: str):
    try:
        es.delete(index=ES_INDEX, id=product_id, ignore=[404])
    except Exception as e:
        print(f"[ES] delete error: {e}")


# ── App startup ───────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup():
    _migrate_images_column()  # ensure all columns exist before re-indexing
    # Create ES index with mapping if it doesn't exist
    for attempt in range(12):
        try:
            if not es.indices.exists(index=ES_INDEX):
                es.indices.create(index=ES_INDEX, body=ES_MAPPING)
                print("[ES] Index created")
            else:
                print("[ES] Index already exists")
            break
        except Exception as e:
            print(f"[ES] not ready yet ({e}), retrying...")
            time.sleep(5)

    # Sync all existing products into ES on boot
    db = SessionLocal()
    try:
        for p in db.query(Product).all():
            es_index(p)
        print("[ES] Existing products synced")
    finally:
        db.close()

    # Init RabbitMQ channel
    get_channel()


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/hello")
def hello():
    return {"message": "Product Service running"}


@app.post("/products", status_code=201)
def create_product(data: dict, user=Depends(verify_token)):
    if user.get("role") != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can add products")

    required = ["name", "price"]
    for field in required:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"'{field}' is required")

    db = SessionLocal()
    try:
        images = data.get("images", [])
        if not isinstance(images, list) or len(images) < 1:
            raise HTTPException(status_code=400, detail="At least 1 product image is required")
        if len(images) > 3:
            raise HTTPException(status_code=400, detail="Maximum 3 product images allowed")
        product = Product(
            name=data["name"],
            description=data.get("description", ""),
            price=float(data["price"]),
            vendor_id=user["sub"],
            category_id=data.get("category_id"),
            stock=int(data.get("stock", 0)),
            images=json.dumps(images),
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        es_index(product)
        r.delete("products")           # Bust the list cache
        return {"message": "Product created", "id": product.id}
    finally:
        db.close()


@app.get("/products")
def get_products(
    request:    Request,
    min_price:  float = None,
    max_price:  float = None,
    min_rating: float = None,
    category_id:str   = None,
    sort_by:    str   = "newest",
):
    rate_limit(request)
    has_filters = any([min_price, max_price, min_rating, category_id, sort_by not in ("newest", "relevance")])
    if not has_filters:
        cached = r.get("products")
        if cached:
            return json.loads(cached)
    db = SessionLocal()
    try:
        q = db.query(Product)
        if min_price  is not None: q = q.filter(Product.price      >= min_price)
        if max_price  is not None: q = q.filter(Product.price      <= max_price)
        if min_rating is not None: q = q.filter(Product.avg_rating >= min_rating)
        if category_id:            q = q.filter(Product.category_id == category_id)
        if sort_by == "price_asc":    q = q.order_by(Product.price.asc())
        elif sort_by == "price_desc": q = q.order_by(Product.price.desc())
        elif sort_by == "rating_desc":q = q.order_by(Product.avg_rating.desc())
        else:                         q = q.order_by(Product.created_at.desc().nullslast())
        products = q.all()
        data = [product_dict(p) for p in products]
        if not has_filters:
            r.set("products", json.dumps(data), ex=60)
        return data
    finally:
        db.close()


@app.get("/products/{product_id}")
def get_product(product_id: str, request: Request):
    rate_limit(request)

    cached = r.get(f"product:{product_id}")
    if cached:
        return json.loads(cached)

    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        data = product_dict(product)
        r.set(f"product:{product_id}", json.dumps(data), ex=60)

        # Publish view event for analytics (fire-and-forget)
        try:
            ch = get_channel()
            if ch:
                ch.basic_publish(
                    exchange="",
                    routing_key="product_view",
                    body=json.dumps({"product_id": str(product.id)}),
                    properties=pika.BasicProperties(delivery_mode=2),
                )
        except Exception as e:
            print(f"[RMQ] publish error: {e}")

        return data
    finally:
        db.close()


@app.patch("/products/{product_id}/stock")
def update_stock(product_id: str, data: dict):
    """
    Internal endpoint called by order-service to decrement stock.
    Not exposed through nginx — only reachable service-to-service.
    """
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        qty = int(data.get("quantity", 1))
        if qty > 0:
            # Decrement (normal order)
            if product.stock < qty:
                db.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock. Available: {product.stock}"
                )
            product.stock -= qty
        else:
            # Negative qty = restore stock (order cancellation)
            product.stock += abs(qty)

        product.stock -= qty
        db.commit()
        db.refresh(product)

        # Keep ES and cache in sync
        es_index(product)
        r.delete(f"product:{product_id}")
        r.delete("products")

        return {"product_id": product_id, "remaining_stock": product.stock}
    finally:
        db.close()


@app.put("/products/{product_id}")
def update_product(product_id: str, data: dict, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.vendor_id != user["sub"]:
            raise HTTPException(status_code=403, detail="You don't own this product")

        if "name"        in data: product.name        = data["name"]
        if "description" in data: product.description = data["description"]
        if "price"       in data: product.price        = float(data["price"])
        if "stock"       in data: product.stock        = int(data["stock"])
        if "category_id" in data: product.category_id  = data["category_id"]
        if "images"      in data:
            imgs = data["images"]
            if not isinstance(imgs, list) or len(imgs) < 1:
                raise HTTPException(status_code=400, detail="At least 1 image required")
            if len(imgs) > 3:
                raise HTTPException(status_code=400, detail="Maximum 3 images allowed")
            product.images = json.dumps(imgs)

        db.commit()
        db.refresh(product)

        es_index(product)
        r.delete(f"product:{product_id}")
        r.delete("products")

        return {"message": "Product updated", **product_dict(product)}
    finally:
        db.close()


def delete_product(product_id: str, user=Depends(verify_token)):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        # Admin can delete any product, vendors only their own
        if user.get("role") != "admin" and product.vendor_id != user["sub"]:
            raise HTTPException(status_code=403, detail="You don't own this product")
        db.delete(product)
        db.commit()
        es_delete(product_id)
        r.delete(f"product:{product_id}")
        r.delete("products")
    finally:
        db.close()


@app.get("/my-products")
def my_products(user=Depends(verify_token)):
    if user.get("role") != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors")
    db = SessionLocal()
    try:
        products = db.query(Product).filter(
            Product.vendor_id == user["sub"]
        ).all()
        return [product_dict(p) for p in products]
    finally:
        db.close()


@app.post("/categories", status_code=201)
def create_category(data: dict, user=Depends(verify_token)):
    if not data.get("name"):
        raise HTTPException(status_code=400, detail="Category name required")
    db = SessionLocal()
    try:
        cat = Category(name=data["name"], parent_id=data.get("parent_id"))
        db.add(cat)
        db.commit()
        return {"message": "Category created", "id": cat.id}
    finally:
        db.close()


@app.get("/categories")
def get_categories():
    db = SessionLocal()
    try:
        cats = db.query(Category).all()
        return [{"id": c.id, "name": c.name, "parent_id": c.parent_id} for c in cats]
    finally:
        db.close()


@app.get("/category/{category_id}")
def products_by_category(category_id: str):
    db = SessionLocal()
    try:
        cats = db.query(Category).filter(
            (Category.id == category_id) | (Category.parent_id == category_id)
        ).all()
        ids = [c.id for c in cats]
        products = db.query(Product).filter(Product.category_id.in_(ids)).all()
        return [product_dict(p) for p in products]
    finally:
        db.close()


# ── Reviews ───────────────────────────────────────────────────────────────────

def review_dict(rv: Review) -> dict:
    return {
        "id":         rv.id,
        "user_id":    rv.user_id,
        "user_name":  rv.user_name,
        "title":      rv.title,
        "comment":    rv.comment,
        "rating":     rv.rating,
        "photo_urls": json.loads(rv.photo_urls or "[]"),
        "created_at": rv.created_at.isoformat() if rv.created_at else None,
    }


def _user_bought_product(user_id: str, product_id: str, token: str) -> bool:
    """Ask order-service whether this user has a DELIVERED order with this product."""
    try:
        resp = requests.get(
            f"{ORDER_SERVICE_URL}/orders",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.status_code != 200:
            return False
        orders = resp.json()
        delivered = [o for o in orders if o.get("status") == "DELIVERED"]
        if not delivered:
            return False
        # Fetch each delivered order's items and check for the product
        for order in delivered:
            detail = requests.get(
                f"{ORDER_SERVICE_URL}/orders/{order['order_id']}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5,
            )
            if detail.status_code != 200:
                continue
            items = detail.json().get("items", [])
            if any(str(i.get("product_id")) == str(product_id) for i in items):
                return True
    except Exception as e:
        print(f"[Review] order-service check failed: {e}")
    return False


@app.post("/products/{product_id}/reviews", status_code=201)
def create_review(product_id: str, data: dict, request: Request, user=Depends(verify_token)):
    # Verify buyer
    token = request.headers.get("authorization", "").split(" ")[-1]
    if not _user_bought_product(user["sub"], product_id, token):
        raise HTTPException(
            status_code=403,
            detail="Only verified buyers with a delivered order can review this product",
        )

    # Validate fields
    rating = data.get("rating")
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be an integer between 1 and 5")
    if not data.get("title", "").strip():
        raise HTTPException(status_code=400, detail="Review title is required")
    if not data.get("comment", "").strip():
        raise HTTPException(status_code=400, detail="Review comment is required")

    photo_urls = data.get("photo_urls", [])
    if not isinstance(photo_urls, list):
        raise HTTPException(status_code=400, detail="photo_urls must be a list")

    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Enforce one review per user per product
        existing = db.query(Review).filter(
            Review.product_id == product_id,
            Review.user_id == user["sub"],
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="You have already reviewed this product")

        review = Review(
            product_id=product_id,
            user_id=user["sub"],
            user_name=user.get("email", "Anonymous"),
            title=data["title"].strip(),
            comment=data["comment"].strip(),
            rating=rating,
            photo_urls=json.dumps(photo_urls),
        )
        db.add(review)

        # Recalculate avg_rating and review_count
        product.review_count = (product.review_count or 0) + 1
        product.avg_rating = (
            ((product.avg_rating or 0.0) * (product.review_count - 1)) + rating
        ) / product.review_count

        db.commit()
        db.refresh(review)

        # Bust product cache so avg_rating is fresh
        r.delete(f"product:{product_id}")
        r.delete("products")
        es_index(product)

        return {"message": "Review submitted", "review": review_dict(review)}
    finally:
        db.close()


@app.get("/products/{product_id}/reviews")
def get_reviews(product_id: str):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        reviews = (
            db.query(Review)
            .filter(Review.product_id == product_id)
            .order_by(Review.created_at.desc())
            .all()
        )
        return {
            "product_id":   product_id,
            "avg_rating":   round(product.avg_rating or 0.0, 1),
            "review_count": product.review_count or 0,
            "reviews":      [review_dict(rv) for rv in reviews],
        }
    finally:
        db.close()


# ── Migration helper: add images column if missing ────────────────────────────
def _migrate_images_column():
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS images TEXT DEFAULT '[]'"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS avg_rating FLOAT DEFAULT 0.0"))
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS review_count INTEGER DEFAULT 0"))
            conn.commit()
        except Exception as e:
            print(f"[Migration] columns: {e}")


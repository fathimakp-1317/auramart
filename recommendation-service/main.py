"""
Recommendation Service API

GET /recommend          — personalised recommendations for logged-in user
GET /recommend/popular  — fallback: most-viewed products (for new users)
GET /hello              — health check
"""
import json, os, time, threading
import redis
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from auth import verify_token
from fastapi import Depends
from matrix import MatrixFactorization
import consumer   # starts background thread on import

app = FastAPI(title="ShopSphere Recommendation Service")
app.add_middleware(GZipMiddleware, minimum_size=1000)

r = redis.Redis(host="redis", port=6379, decode_responses=True)

# Start the RabbitMQ consumer in a background daemon thread
_consumer_thread = threading.Thread(target=consumer.start, daemon=True)
_consumer_thread.start()


def get_model() -> MatrixFactorization:
    """Load the trained MF model from Redis."""
    raw = r.get("mf_model")
    if not raw:
        return None
    return MatrixFactorization.from_json(raw)


@app.get("/hello")
def hello():
    return {"message": "Recommendation Service running"}


@app.get("/recommend/popular")
def popular():
    """
    Returns the most-viewed product IDs from analytics.
    Used as fallback for new users with no purchase history.
    """
    raw = r.get("trending")
    if not raw:
        return []
    return json.loads(raw)


@app.get("/recommend")
def recommend(user=Depends(verify_token)):
    """
    Returns personalised product recommendations for the authenticated user.

    Algorithm:
      1. Check Redis cache for this user's recommendations
      2. If cached — return immediately
      3. Load the trained MF model from Redis
      4. Use model to score all items for this user
      5. Cache result for 5 minutes
      6. If model not trained yet (< 2 users) — fall back to popular
    """
    user_id = str(user["sub"])
    cache_key = f"rec:{user_id}"

    # Check cache first
    cached = r.get(cache_key)
    if cached:
        return {"source": "cache", "recommendations": json.loads(cached)}

    # Load MF model
    model = get_model()

    if model and user_id in model.user_index:
        # Personalised recommendations via Matrix Factorization
        recs = model.recommend(user_id, top_n=10)
        r.set(cache_key, json.dumps(recs), ex=300)   # cache 5 mins
        return {"source": "matrix_factorization", "recommendations": recs}

    # Fallback: user has no purchase history yet — return popular items
    popular_raw = r.get("trending")
    popular = json.loads(popular_raw) if popular_raw else []
    popular_ids = [p["product_id"] for p in popular]
    return {"source": "popular_fallback", "recommendations": popular_ids}

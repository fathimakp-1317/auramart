"""
Analytics Service API

Merges api.py + main.py into one clean FastAPI app.
Consumer runs as a background thread.

Endpoints:
  GET /trending          — top 10 most-viewed products (with scores)
  GET /trending/{n}      — top N products (max 50)
  GET /stats/{product_id}— view count for a specific product
  GET /hello             — health check
"""
import json, threading
import redis
from fastapi import FastAPI, Path
from fastapi.middleware.gzip import GZipMiddleware
import consumer   # starts background consumer thread on import

app = FastAPI(title="ShopSphere Analytics Service")
app.add_middleware(GZipMiddleware, minimum_size=1000)

r = redis.Redis(host="redis", port=6379, decode_responses=True)

TRENDING_KEY = "trending_zset"

# Start consumer in background daemon thread
_thread = threading.Thread(target=consumer.start, daemon=True)
_thread.start()


@app.get("/hello")
def hello():
    return {"message": "Analytics Service running"}


@app.get("/trending")
def trending():
    """
    Top 10 most-viewed products, ranked by view count descending.
    Reads from Redis sorted set — O(log N), not O(N) key scan.
    """
    top = r.zrevrange(TRENDING_KEY, 0, 9, withscores=True)
    return [
        {"product_id": pid, "views": int(score)}
        for pid, score in top
    ]


@app.get("/trending/{n}")
def trending_n(n: int = Path(ge=1, le=50)):
    """Top N trending products (max 50)."""
    top = r.zrevrange(TRENDING_KEY, 0, n - 1, withscores=True)
    return [
        {"product_id": pid, "views": int(score)}
        for pid, score in top
    ]


@app.get("/stats/{product_id}")
def product_stats(product_id: str):
    """View count for a specific product."""
    score = r.zscore(TRENDING_KEY, product_id)
    return {
        "product_id": product_id,
        "views":      int(score) if score else 0,
    }

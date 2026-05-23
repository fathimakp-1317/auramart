"""
Search Service — ElasticSearch powered full-text + fuzzy search.

Replaces the old in-memory Python string filter with real ES queries:
  - Multi-field full-text search across name + description
  - Fuzzy matching (handles typos: "iphne" → iPhone)
  - Price range filter
  - Category filter
  - Relevance-ranked results (ES _score)
  - Redis cache for repeated identical queries
"""
import json, os, time
import redis
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from elasticsearch import Elasticsearch

app = FastAPI(title="ShopSphere Search Service")
app.add_middleware(GZipMiddleware, minimum_size=1000)

ES_URL   = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
ES_INDEX = "products"

es = Elasticsearch(ES_URL)
r  = redis.Redis(host="redis", port=6379, decode_responses=True)

CACHE_TTL = 30   # seconds — short TTL so new products appear quickly


@app.on_event("startup")
def startup():
    """Wait until ES is reachable before accepting traffic."""
    for attempt in range(20):
        try:
            if es.ping():
                print("[search] Elasticsearch is ready")
                return
        except Exception:
            pass
        print(f"[search] Waiting for Elasticsearch... ({attempt + 1}/20)")
        time.sleep(3)
    print("[search] Warning: Elasticsearch not reachable at startup")


@app.get("/hello")
def hello():
    return {"message": "Search Service running"}


@app.get("/search")
def search(
    q:           str   = Query(...,  min_length=1, description="Search term"),
    min_price:   float = Query(None, description="Minimum price filter"),
    max_price:   float = Query(None, description="Maximum price filter"),
    min_rating:  float = Query(None, description="Minimum avg_rating filter"),
    category_id: str   = Query(None, description="Filter by category ID"),
    sort_by:     str   = Query("relevance", description="Sort: relevance|price_asc|price_desc|rating_desc|newest"),  # default: relevance avoids created_at dependency
    page:        int   = Query(1,    ge=1,         description="Page number"),
    size:        int   = Query(20,   ge=1, le=100, description="Results per page"),
):
    # ── Cache key includes every parameter ───────────────────────────────────
    cache_key = f"search:{q}:{min_price}:{max_price}:{min_rating}:{category_id}:{sort_by}:{page}:{size}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # ── Build the ES query ────────────────────────────────────────────────────
    must_clauses = [
        {
            # multi_match searches both name and description
            # fuzziness AUTO: handles typos up to 2 chars on longer words
            # name^3 boosts name matches 3× over description matches
            "multi_match": {
                "query":     q,
                "fields":    ["name^3", "description"],
                "fuzziness": "AUTO",
                "operator":  "or",
            }
        }
    ]

    filter_clauses = [
        # Only return products that are actually in stock
        {"range": {"stock": {"gt": 0}}}
    ]

    if min_price is not None or max_price is not None:
        price_range = {}
        if min_price is not None: price_range["gte"] = min_price
        if max_price is not None: price_range["lte"] = max_price
        filter_clauses.append({"range": {"price": price_range}})

    if min_rating is not None:
        filter_clauses.append({"range": {"avg_rating": {"gte": min_rating}}})

    if category_id:
        filter_clauses.append({"term": {"category_id": category_id}})

    es_query = {
        "query": {
            "bool": {
                "must":   must_clauses,
                "filter": filter_clauses,
            }
        },
        # Return relevance score so frontend can optionally display it
        "sort": (
            [{"price": {"order": "asc"}},  "_score"] if sort_by == "price_asc"  else
            [{"price": {"order": "desc"}}, "_score"] if sort_by == "price_desc" else
            [{"avg_rating": {"order": "desc", "missing": "_last"}}, "_score"] if sort_by == "rating_desc" else
            [{"created_at": {"order": "desc", "missing": "_last"}}, "_score"] if sort_by == "newest" else
            ["_score"]  # relevance default
        ),
        "from": (page - 1) * size,
        "size": size,
        # Only return the fields we need — saves bandwidth
        "_source": ["id", "name", "description", "price", "stock",
                    "vendor_id", "category_id", "avg_rating", "review_count", "images"],
    }

    # ── Execute ───────────────────────────────────────────────────────────────
    try:
        resp = es.search(index=ES_INDEX, body=es_query)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Search unavailable: {e}")

    hits      = resp["hits"]["hits"]
    total     = resp["hits"]["total"]["value"]
    results   = [{"score": h["_score"], **h["_source"]} for h in hits]

    response = {
        "query":   q,
        "total":   total,
        "page":    page,
        "size":    size,
        "pages":   (total + size - 1) // size,
        "results": results,
    }

    r.set(cache_key, json.dumps(response), ex=CACHE_TTL)
    return response


@app.get("/suggest")
def suggest(q: str = Query(..., min_length=1)):
    """
    Autocomplete / prefix suggestions.
    Returns up to 5 product names that start with the typed prefix.
    Used by the search bar dropdown.
    """
    cache_key = f"suggest:{q}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    es_query = {
        "query": {
            "bool": {
                "should": [
                    {"match_phrase_prefix": {"name": {"query": q, "max_expansions": 10}}},
                    {"fuzzy": {"name": {"value": q, "fuzziness": "AUTO"}}},
                ],
                "filter": [{"range": {"stock": {"gt": 0}}}],
            }
        },
        "_source": ["id", "name", "price"],
        "size": 5,
    }

    try:
        resp = es.search(index=ES_INDEX, body=es_query)
        suggestions = [h["_source"] for h in resp["hits"]["hits"]]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Suggest unavailable: {e}")

    r.set(cache_key, json.dumps(suggestions), ex=15)
    return suggestions

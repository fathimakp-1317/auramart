import redis, os
from fastapi import Request, HTTPException

r = redis.Redis(host="redis", port=6379, decode_responses=True)

LIMIT  = 100   # requests
WINDOW = 60    # seconds

def rate_limit(request: Request):
    ip  = request.client.host
    key = f"rate:{ip}"
    pipe = r.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, WINDOW)
    results = pipe.execute()
    count = results[0]
    if count > LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests — slow down")

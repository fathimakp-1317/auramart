"""
Notification API — serves stored notifications to the frontend.

Endpoints:
  GET  /notifications          — all notifications for logged-in user
  GET  /notifications/unread   — count of unread notifications
  POST /notifications/read     — mark all notifications as read
  POST /notifications/read/{i} — mark a single notification as read
  DELETE /notifications        — clear all notifications
"""
import json
import redis
from fastapi import FastAPI, Depends
from fastapi.middleware.gzip import GZipMiddleware
from auth import verify_token

app = FastAPI(title="ShopSphere Notification API")
app.add_middleware(GZipMiddleware, minimum_size=1000)

r = redis.Redis(host="redis", port=6379, decode_responses=True)


def get_notifications(user_id: str) -> list:
    raw = r.get(f"notify:{user_id}")
    return json.loads(raw) if raw else []

def save_notifications(user_id: str, notifications: list):
    r.set(f"notify:{user_id}", json.dumps(notifications))


@app.get("/hello")
def hello():
    return {"message": "Notification API running"}


@app.get("/notifications")
def list_notifications(user=Depends(verify_token)):
    """All notifications for the logged-in user, newest first."""
    return get_notifications(user["sub"])


@app.get("/notifications/unread")
def unread_count(user=Depends(verify_token)):
    """Count of unread notifications — used for the navbar badge."""
    notifications = get_notifications(user["sub"])
    count = sum(1 for n in notifications if not n.get("read", False))
    return {"unread": count}


@app.post("/notifications/read")
def mark_all_read(user=Depends(verify_token)):
    """Mark every notification as read."""
    notifications = get_notifications(user["sub"])
    for n in notifications:
        n["read"] = True
    save_notifications(user["sub"], notifications)
    return {"message": f"Marked {len(notifications)} notifications as read"}


@app.post("/notifications/read/{index}")
def mark_one_read(index: int, user=Depends(verify_token)):
    """Mark a single notification as read by index."""
    notifications = get_notifications(user["sub"])
    if index < 0 or index >= len(notifications):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Notification not found")
    notifications[index]["read"] = True
    save_notifications(user["sub"], notifications)
    return {"message": "Notification marked as read"}


@app.delete("/notifications")
def clear_notifications(user=Depends(verify_token)):
    """Clear all notifications for this user."""
    r.delete(f"notify:{user['sub']}")
    return {"message": "All notifications cleared"}

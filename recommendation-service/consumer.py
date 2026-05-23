"""
RabbitMQ Consumer — runs as background thread inside the container.

Listens on 'order_created' queue. On each event:
  1. Stores which products this user bought (in Redis)
  2. Rebuilds the Matrix Factorization model across ALL users
  3. Saves the trained model to Redis so /recommend can serve it

Why retrain on every order?
  In production you'd batch-retrain on a schedule. Here we retrain
  on each order so recommendations update immediately after a purchase
  — which is the right behaviour for a demo/assessment.
"""
import json, time, threading
import pika
import redis
from matrix import MatrixFactorization

r = redis.Redis(host="redis", port=6379, decode_responses=True)

_train_lock = threading.Lock()   # prevent concurrent retrains


def load_interactions() -> dict:
    """Load all user→product interactions from Redis."""
    interactions = {}
    keys = r.keys("user_products:*")
    for key in keys:
        user_id = key.split(":", 1)[1]
        raw = r.get(key)
        if raw:
            interactions[user_id] = json.loads(raw)
    return interactions


def retrain():
    """Rebuild and save the MF model. Thread-safe."""
    with _train_lock:
        interactions = load_interactions()
        if len(interactions) < 2:
            # Need at least 2 users to find collaborative patterns
            print("[consumer] Not enough users to train MF model yet")
            return

        print(f"[consumer] Training MF on {len(interactions)} users...")
        mf = MatrixFactorization(k=10, lr=0.01, reg=0.02, epochs=20)
        mf.fit(interactions)
        r.set("mf_model", mf.to_json())
        print("[consumer] MF model saved to Redis")


def on_order_created(ch, method, properties, body):
    try:
        event  = json.loads(body)
        user_id = str(event.get("user_id", ""))
        items   = event.get("items", [])

        if not user_id or not items:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # 1. Load existing purchases for this user
        existing_raw = r.get(f"user_products:{user_id}")
        existing = set(json.loads(existing_raw)) if existing_raw else set()

        # 2. Add new products from this order
        new_products = {str(i["product_id"]) for i in items}
        updated = existing | new_products

        # 3. Persist
        r.set(f"user_products:{user_id}", json.dumps(list(updated)))

        # 4. Invalidate stale recommendations for this user
        r.delete(f"rec:{user_id}")

        print(f"[consumer] User {user_id} now has {len(updated)} purchased products")

        # 5. Retrain MF model
        retrain()

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[consumer] Error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start():
    connection = None
    for _ in range(15):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="rabbitmq")
            )
            break
        except Exception:
            print("[consumer] Waiting for RabbitMQ...")
            time.sleep(3)

    if not connection:
        print("[consumer] Could not connect to RabbitMQ — exiting")
        return

    channel = connection.channel()
    channel.queue_declare(queue="order_created", durable=True)
    channel.basic_qos(prefetch_count=1)   # process one at a time
    channel.basic_consume(
        queue="order_created",
        on_message_callback=on_order_created,
    )
    print("[consumer] Listening on order_created queue...")
    channel.start_consuming()


if __name__ == "__main__":
    start()

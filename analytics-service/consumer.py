"""
Analytics Consumer — listens on 'product_view' queue.

On each event:
  1. Increments the view count for that product (Redis ZINCRBY)
  2. Updates the sorted set 'trending' so /trending is always O(log N)
  3. Writes the top-10 trending list to 'trending' key so
     recommendation-service can read it without hitting the API

Uses manual ack so a crash doesn't silently drop view events.
"""
import json, time
import pika
import redis

r = redis.Redis(host="redis", port=6379, decode_responses=True)

TRENDING_KEY  = "trending_zset"   # sorted set: product_id → view count
TRENDING_SNAP = "trending"        # JSON snapshot for recommendation-service


def update_trending_snapshot():
    """
    Write the top-10 trending products as a JSON list to Redis.
    recommendation-service reads this key for its /recommend/popular fallback.
    """
    top = r.zrevrange(TRENDING_KEY, 0, 9, withscores=True)
    snapshot = [{"product_id": pid, "score": int(score)} for pid, score in top]
    r.set(TRENDING_SNAP, json.dumps(snapshot))


def on_product_view(ch, method, properties, body):
    try:
        data       = json.loads(body)
        product_id = str(data.get("product_id", ""))

        if not product_id:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Atomic increment in sorted set — O(log N)
        r.zincrby(TRENDING_KEY, 1, product_id)

        # Update snapshot for recommendation-service
        update_trending_snapshot()

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[analytics consumer] Error: {e}")
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
            print("[analytics] Waiting for RabbitMQ...")
            time.sleep(3)

    if not connection:
        print("[analytics] Could not connect to RabbitMQ — exiting")
        return

    channel = connection.channel()
    channel.queue_declare(queue="product_view", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue="product_view",
        on_message_callback=on_product_view,
    )
    print("[analytics] Listening on product_view queue...")
    channel.start_consuming()


if __name__ == "__main__":
    start()

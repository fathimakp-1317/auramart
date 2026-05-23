"""
Background consumer — runs as a separate process inside the product-service container.
Listens on the 'order_created' queue and decrements stock for each item ordered.
This gives us the event-driven inventory update the requirement calls for.
"""
import json, time, os
import pika
import redis
from database import SessionLocal
from models import Product
from elasticsearch import Elasticsearch

ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
es = Elasticsearch(ES_URL)
r  = redis.Redis(host="redis", port=6379, decode_responses=True)


def on_order_created(ch, method, properties, body):
    try:
        event = json.loads(body)
        items = event.get("items", [])

        db = SessionLocal()
        try:
            for item in items:
                product = db.query(Product).filter(
                    Product.id == str(item["product_id"])
                ).first()

                if not product:
                    print(f"[consumer] Product {item['product_id']} not found, skipping")
                    continue

                qty = int(item.get("quantity", 1))
                if product.stock >= qty:
                    product.stock -= qty
                else:
                    print(f"[consumer] Warning: insufficient stock for {product.id}, setting to 0")
                    product.stock = 0

            db.commit()

            # Bust Redis cache and re-index in ES for all affected products
            for item in items:
                pid = str(item["product_id"])
                r.delete(f"product:{pid}")
                r.delete("products")
                # Re-fetch and re-index
                product = db.query(Product).filter(Product.id == pid).first()
                if product:
                    try:
                        es.index(index="products", id=pid, document={
                            "id": pid, "name": product.name,
                            "description": product.description,
                            "price": product.price, "stock": product.stock,
                            "vendor_id": product.vendor_id,
                            "category_id": product.category_id,
                        })
                    except Exception as e:
                        print(f"[consumer] ES update error: {e}")

            print(f"[consumer] Order {event.get('order_id')} processed, stock updated")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        finally:
            db.close()

    except Exception as e:
        print(f"[consumer] Error processing order: {e}")
        # Negative-ack so the message goes back to the queue
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def main():
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
        print("[consumer] Could not connect to RabbitMQ, exiting")
        return

    channel = connection.channel()
    channel.queue_declare(queue="order_created", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="order_created", on_message_callback=on_order_created)
    print("[consumer] Listening for orders...")
    channel.start_consuming()


if __name__ == "__main__":
    main()

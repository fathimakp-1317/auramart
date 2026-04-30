import pika
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


# ─── Connect to RabbitMQ ──────────────────────────────────
def get_connection():
    """
    Create a connection to RabbitMQ.
    Returns connection and channel.
    """
    connection = pika.BlockingConnection(
        pika.URLParameters(
            os.getenv("RABBITMQ_URL",
                      "amqp://guest:guest@localhost:5672/")
        )
    )
    channel = connection.channel()
    return connection, channel


# ─── Declare Queues ───────────────────────────────────────
def setup_queues(channel):
    """
    Create queues if they don't exist.
    durable=True means queues survive RabbitMQ restarts.
    """
    channel.queue_declare(
        queue="order.completed",
        durable=True
    )

    channel.queue_declare(
        queue="inventory.updated",
        durable=True
    )


# ─── Publish: Order Completed ─────────────────────────────
def publish_order_completed(order_id: str,
                             user_id: str,
                             items: list):
    """
    Send order.completed event to RabbitMQ.
    recommendation-service will receive this
    and update the user_interactions table.

    items format:
    [
        {"product_id": "uuid", "quantity": 2},
        {"product_id": "uuid", "quantity": 1}
    ]
    """
    connection, channel = get_connection()
    setup_queues(channel)

    # build the event payload
    event = {
        "event":     "order.completed",
        "order_id":  str(order_id),
        "user_id":   str(user_id),
        "items":     items,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # publish to RabbitMQ
    channel.basic_publish(
        exchange="",
        routing_key="order.completed",
        body=json.dumps(event),
        properties=pika.BasicProperties(
            delivery_mode=2  # makes message persistent
            # even if RabbitMQ crashes, message is not lost
        )
    )

    print(f"Published order.completed: {order_id}")
    connection.close()


# ─── Publish: Inventory Update Request ───────────────────
def publish_inventory_check(product_id: str,
                              quantity_needed: int):
    """
    Send a request to check/reserve inventory
    before confirming an order.
    """
    connection, channel = get_connection()
    setup_queues(channel)

    event = {
        "event":           "inventory.check",
        "product_id":      str(product_id),
        "quantity_needed": quantity_needed,
        "timestamp":       datetime.utcnow().isoformat() + "Z"
    }

    channel.basic_publish(
        exchange="",
        routing_key="inventory.updated",
        body=json.dumps(event),
        properties=pika.BasicProperties(
            delivery_mode=2
        )
    )

    print(f"Published inventory.check: {product_id}")
    connection.close()
import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()


def on_inventory_updated(ch, method, properties, body):
    """
    We use this to update our local inventory
    quantity after an order is processed.
    """
    event = json.loads(body)

    print(f"Received inventory.updated event:")
    print(f"  product_id:   {event['product_id']}")
    print(f"  new_quantity: {event['new_quantity']}")
    print(f"  timestamp:    {event['timestamp']}")

    # Week 3 — we will update the inventory table here
    # for now just acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer():
    """
    Start listening for inventory.updated events.
    This runs as a background process.
    """
    connection = pika.BlockingConnection(
        pika.URLParameters(
            os.getenv("RABBITMQ_URL",
                      "amqp://guest:guest@localhost:5672/")
        )
    )
    channel = connection.channel()

    # make sure queue exists
    channel.queue_declare(
        queue="inventory.updated",
        durable=True
    )

    # only receive 1 message at a time
    channel.basic_qos(prefetch_count=1)

    # start listening
    channel.basic_consume(
        queue="inventory.updated",
        on_message_callback=on_inventory_updated
    )

    print("Listening for inventory.updated events...")
    channel.start_consuming()


if __name__ == "__main__":
    start_consumer()
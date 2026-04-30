from django.core.management.base import BaseCommand
from apps.inventory.events import publish_order_completed


class Command(BaseCommand):
    help = "Test RabbitMQ connection by publishing a test event"

    def handle(self, *args, **options):
        self.stdout.write("Testing RabbitMQ connection...")

        try:
            publish_order_completed(
                order_id="test-order-123",
                user_id="test-user-456",
                items=[
                    {
                        "product_id": "test-product-789",
                        "quantity":   2
                    }
                ]
            )
            self.stdout.write(
                self.style.SUCCESS(
                    " RabbitMQ test successful!"
                    " Check http://localhost:15672"
                    " to see the message."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f" RabbitMQ connection failed: {e}"
                    "\nMake sure RabbitMQ is running."
                )
            )
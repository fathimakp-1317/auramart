"""
RabbitMQ Event Contracts
========================
This file documents all events published
and consumed by the order-service.
"""

# ─── Events We PUBLISH ────────────────────────────────────

ORDER_COMPLETED_EVENT = {
    "event":     "order.completed",
    "order_id":  "uuid string",
    "user_id":   "uuid string",
    "items": [
        {
            "product_id": "uuid string",
            "quantity":   "integer"
        }
    ],
    "timestamp": "ISO8601 datetime string"
}

INVENTORY_CHECK_EVENT = {
    "event":           "inventory.check",
    "product_id":      "uuid string",
    "quantity_needed": "integer",
    "timestamp":       "ISO8601 datetime string"
}

# ─── Events We CONSUME ────────────────────────────────────

INVENTORY_UPDATED_EVENT = {
    "event":        "inventory.updated",
    "product_id":   "uuid string",
    "new_quantity": "integer",
    "timestamp":    "ISO8601 datetime string"
}

# ─── Queue Names ──────────────────────────────────────────

QUEUES = {
    "we_publish":  "order.completed",
    "we_consume":  "inventory.updated",
}

# ─── Ports & Services ─────────────────────────────────────

SERVICES = {
    "order-service":          "port 5003  (us)",
    "recommendation-service": "port 5004  (Member 4)",
    "rabbitmq-dashboard":     "port 15672 (browser)",
    "rabbitmq-connection":    "port 5672  (app)",
}
# ShopSphere — Interface Contract
> All 4 members must agree on and follow everything in this file.
> Last updated: 29-04-2026

---

## 1. API URL Convention
All endpoints must follow this pattern:
/api/v1/{service}/{resource}

Examples:
- POST /api/v1/auth/login
- GET  /api/v1/products/search
- POST /api/v1/orders/checkout
- GET  /api/v1/recommendations/{user_id}

---

## 2. JWT Token Format
Every protected endpoint expects this header:
  Authorization: Bearer <token>

Token payload:
{
  "sub": "user_id (UUID)",
  "role": "customer | vendor | admin",
  "iat": "issued at (timestamp)",
  "exp": "expires at (timestamp, 24h from iat)"
}

Owner: Member 1

---

## 3. Standard Response Format
Every service must return responses in this shape:

Success:
{
  "success": true,
  "data": { ... }
}

Error:
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "readable message"
  }
}

---

## 4. RabbitMQ Events

### Event: order.completed
Published by: Service C (Member 3)
Consumed by: Service D (Member 4)
Queue name: order.completed

Payload:
{
  "event": "order.completed",
  "order_id": "uuid",
  "user_id": "uuid",
  "items": [
    {
      "product_id": "uuid",
      "quantity": 2
    }
  ],
  "timestamp": "ISO8601"
}

### Event: inventory.updated
Published by: Service D (Member 4)
Consumed by: Service C (Member 3)
Queue name: inventory.updated

Payload:
{
  "event": "inventory.updated",
  "product_id": "uuid",
  "new_quantity": 48,
  "timestamp": "ISO8601"
}

---

## 5. Service Ports

| Service                 | Port |
**********************************
| auth-service            | 5001 |
| product-service         | 5002 |
| order-service           | 5003 |
| recommendation-service  | 5004 |

---

## 6. Cross-Service Rules
- Never create foreign keys across services
- Always pass user_id from the JWT — never trust the request body for identity
- All UUIDs are strings (not integers)

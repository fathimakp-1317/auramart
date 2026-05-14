# ShopSphere Order Service API Documentation

Version: 1.0
Port: 5003
Base URL: http://localhost:5003

---

## Authentication
All requests should include user_id.
In production this comes from JWT token
provided by auth-service (port 5001).

---

## Health Check

GET /health/

Response:
{
    "success": true,
    "data": {
        "service": "order-service",
        "status": "running",
        "port": 5003
    }
}

---

## Cart Endpoints

### Get Cart
GET /api/v1/cart/{user_id}/

Response:
{
    "success": true,
    "data": {
        "user_id": "string",
        "items": [
            {
                "product_id": "string",
                "quantity": 2,
                "price": 29.99,
                "subtotal": 59.98
            }
        ],
        "total": 59.98
    }
}

### Add Item to Cart
POST /api/v1/cart/{user_id}/add/

Request:
{
    "product_id": "string",
    "quantity": 2,
    "price": 29.99,
    "vendor_id": "string"
}

### Update Item Quantity
PATCH /api/v1/cart/{user_id}/update/{product_id}/

Request:
{ "quantity": 5 }

### Remove Item
DELETE /api/v1/cart/{user_id}/remove/{product_id}/

### Clear Cart
DELETE /api/v1/cart/{user_id}/clear/

---

## Order Endpoints

### Place Order (Main Endpoint)
POST /api/v1/orders/place/

Request:
{ "user_id": "string" }

Response:
{
    "success": true,
    "data": {
        "order_id": "uuid",
        "user_id": "string",
        "status": "pending",
        "total_amount": 59.98,
        "items": [...],
        "payment": {
            "payment_intent_id": "pi_...",
            "client_secret": "pi_...secret",
            "currency": "usd"
        }
    }
}

### Checkout (Without Stripe)
POST /api/v1/orders/checkout/

Request:
{ "user_id": "string" }

### Get All Orders (Admin)
GET /api/v1/orders/all/

### Get User Orders
GET /api/v1/orders/user/{user_id}/

### Get Single Order
GET /api/v1/orders/{order_id}/

### Update Order Status
PATCH /api/v1/orders/{order_id}/status/

Request:
{ "status": "shipped" }

Status options:
pending → paid → shipped → delivered → cancelled

### Cancel Order
PATCH /api/v1/orders/{order_id}/cancel/

---

## Inventory Endpoints

### Add Product to Inventory
POST /api/v1/inventory/add/

Request:
{
    "product_id": "string",
    "quantity": 100
}

### Get All Inventory
GET /api/v1/inventory/all/

### Get Product Inventory
GET /api/v1/inventory/{product_id}/

### Check Stock
GET /api/v1/inventory/{product_id}/check/?quantity=5

Response:
{
    "success": true,
    "data": {
        "product_id": "string",
        "quantity_needed": 5,
        "quantity_in_stock": 20,
        "is_available": true,
        "version": 3
    }
}

### Restock Product
PATCH /api/v1/inventory/{product_id}/restock/

Request:
{ "quantity_to_add": 50 }

### Reduce Stock
PATCH /api/v1/inventory/{product_id}/reduce/

Request:
{
    "quantity": 2,
    "current_version": 3
}

### Get Low Stock Products
GET /api/v1/inventory/low-stock/

---

## Payment Endpoints

### Initiate Payment
POST /api/v1/payments/{order_id}/initiate/

Response:
{
    "success": true,
    "data": {
        "order_id": "uuid",
        "total_amount": 59.98,
        "payment_intent_id": "pi_...",
        "client_secret": "pi_...secret",
        "currency": "usd"
    }
}

### Verify Payment
POST /api/v1/payments/{order_id}/verify/

Request:
{ "payment_intent_id": "pi_..." }

### Get Payment Status
GET /api/v1/payments/{order_id}/status/

### Refund Payment
POST /api/v1/payments/{order_id}/refund/

### Stripe Webhook
POST /api/v1/payments/webhook/

---

## Frontend Pages

Cart:         http://localhost:5003/pages/cart/
Checkout:     http://localhost:5003/pages/checkout/
Orders:       http://localhost:5003/pages/orders/
Order Detail: http://localhost:5003/pages/order-detail/?id={order_id}

---

## Error Response Format

{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable message"
    }
}

Common Error Codes:
- VALIDATION_ERROR    → Invalid request data
- MISSING_FIELDS      → Required fields missing
- INSUFFICIENT_STOCK  → Not enough stock
- VERSION_CONFLICT    → Race condition detected
- ORDER_CANCELLED     → Order is cancelled
- ALREADY_PAID        → Order already paid
- NOT_FOUND           → Resource not found
- SERVER_ERROR        → Internal server error

---

## Architecture

Service:    Django REST Framework
Database:   PostgreSQL
Cache:      Redis (cart storage)
Queue:      RabbitMQ (order events)
Tasks:      Celery (background jobs)
Payments:   Stripe
Port:       5003

Related Services:
- Auth Service     → port 5001 (JWT tokens)
- Product Service  → port 5002 (product data)
- Rec Service      → port 5004 (recommendations)
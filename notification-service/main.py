"""
Notification Service
====================
Listens on 'order_created' RabbitMQ queue.
On each order event:
  1. Stores in-app notification in Redis (shown in bell icon)
  2. Sends a real order confirmation email via Gmail SMTP

Environment variables required:
  EMAIL_ADDRESS  — your Gmail address
  EMAIL_PASSWORD — Gmail App Password (16 chars, no spaces)
"""
import json, time, os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from datetime             import datetime, timezone

import pika
import redis
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(host="redis", port=6379, decode_responses=True)

EMAIL_ADDRESS  = os.getenv("EMAIL_ADDRESS",  "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
MAX_NOTIFS     = 50


# ── Email ─────────────────────────────────────────────────────────────────────
def send_email(to_email: str, order_id: int, items: list, total: float):
    """Send HTML order confirmation email via Gmail SMTP."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("[notify] EMAIL_ADDRESS or EMAIL_PASSWORD not set — skipping email")
        return
    if not to_email or "@" not in to_email:
        print(f"[notify] Invalid email address: {to_email} — skipping")
        return

    # Build items table rows
    rows = ""
    for item in items:
        subtotal = item.get("price", 0) * item.get("quantity", 1)
        rows += f"""
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #1e4435;color:#B0E4CC">{item.get("name", item.get("product_id",""))}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #1e4435;color:#B0E4CC;text-align:center">{item.get("quantity",1)}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #1e4435;color:#408A71;text-align:right">₹{item.get("price",0):,.2f}</td>
          <td style="padding:10px 12px;border-bottom:1px solid #1e4435;color:#B0E4CC;text-align:right">₹{subtotal:,.2f}</td>
        </tr>"""

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#091413;font-family:Georgia,serif">
      <div style="max-width:580px;margin:32px auto;background:#0d1f1d;border:1px solid #285A48;border-radius:16px;overflow:hidden">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#285A48,#408A71);padding:32px;text-align:center">
          <h1 style="margin:0;color:#B0E4CC;font-size:26px;letter-spacing:1px">ShopSphere</h1>
          <p style="margin:6px 0 0;color:#091413;font-size:13px;font-style:italic">Discover · Explore · Buy</p>
        </div>

        <!-- Body -->
        <div style="padding:32px">
          <h2 style="color:#B0E4CC;margin:0 0 6px;font-size:20px">Order Confirmed!</h2>
          <p style="color:#408A71;margin:0 0 24px;font-size:14px">
            Thank you for your purchase. Your order <strong style="color:#B0E4CC">#{order_id}</strong>
            has been placed successfully and is being processed.
          </p>

          <!-- Items table -->
          <table style="width:100%;border-collapse:collapse;margin-bottom:20px">
            <thead>
              <tr style="background:#1e4435">
                <th style="padding:10px 12px;text-align:left;color:#408A71;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Product</th>
                <th style="padding:10px 12px;text-align:center;color:#408A71;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Qty</th>
                <th style="padding:10px 12px;text-align:right;color:#408A71;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Price</th>
                <th style="padding:10px 12px;text-align:right;color:#408A71;font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px">Subtotal</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>

          <!-- Total -->
          <div style="background:#1e4435;border-radius:10px;padding:14px 16px;display:flex;justify-content:space-between;margin-bottom:24px">
            <span style="color:#B0E4CC;font-weight:bold;font-size:15px">Total</span>
            <span style="color:#408A71;font-weight:bold;font-size:18px">₹{total:,.2f}</span>
          </div>

          <!-- Info -->
          <p style="color:#285A48;font-size:13px;line-height:1.6;margin:0">
            You can track your order status anytime from the
            <a href="http://localhost/orders" style="color:#408A71">Orders</a> section.
            We'll notify you when your order is shipped.
          </p>
        </div>

        <!-- Footer -->
        <div style="background:#091413;padding:20px;text-align:center;border-top:1px solid #285A48">
          <p style="color:#285A48;font-size:12px;margin:0">
            © {datetime.now().year} ShopSphere · This is an automated email, please do not reply.
          </p>
        </div>

      </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Order #{order_id} Confirmed — ShopSphere"
        msg["From"]    = f"ShopSphere <{EMAIL_ADDRESS}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

        print(f"[notify] Email sent to {to_email} for order #{order_id}")

    except smtplib.SMTPAuthenticationError:
        print("[notify] ❌ Gmail authentication failed — check EMAIL_ADDRESS and EMAIL_PASSWORD in .env")
    except smtplib.SMTPException as e:
        print(f"[notify] ❌ SMTP error: {e}")
    except Exception as e:
        print(f"[notify] ❌ Email error: {e}")


# ── RabbitMQ callback ─────────────────────────────────────────────────────────
def on_order_created(ch, method, properties, body):
    try:
        data     = json.loads(body)
        user_id  = str(data.get("user_id", ""))
        email    = data.get("email", "")
        order_id = data.get("order_id")
        items    = data.get("items", [])
        total    = data.get("total", 0)

        if not user_id:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # 1. Store in-app notification in Redis
        notification = {
            "order_id":  order_id,
            "message":   f"Your order #{order_id} has been placed successfully!",
            "total":     total,
            "read":      False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        key = f"notify:{user_id}"
        raw = r.get(key)
        notifications = json.loads(raw) if raw else []
        notifications.insert(0, notification)
        notifications = notifications[:MAX_NOTIFS]
        r.set(key, json.dumps(notifications))
        print(f"[notify] In-app notification stored for user {user_id}")

        # 2. Send confirmation email
        if email:
            send_email(email, order_id, items, total)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[notify] Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def on_order_cancelled(ch, method, properties, body):
    try:
        data     = json.loads(body)
        user_id  = str(data.get("user_id", ""))
        email    = data.get("email", "")
        order_id = data.get("order_id")
        total    = data.get("total", 0)

        if not user_id:
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Store in-app notification
        notification = {
            "order_id":  order_id,
            "message":   f"Order #{order_id} has been cancelled. Refund of ₹{total:,.2f} will be processed in 5-7 business days.",
            "total":     total,
            "read":      False,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        key = f"notify:{user_id}"
        raw = r.get(key)
        notifications = json.loads(raw) if raw else []
        notifications.insert(0, notification)
        r.set(key, json.dumps(notifications[:MAX_NOTIFS]))

        # Send cancellation email
        if email:
            send_cancellation_email(email, order_id, total)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"[notify] Cancel error: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def send_cancellation_email(to_email: str, order_id: int, total: float):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        return
    if not to_email or "@" not in to_email:
        return

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#091413;font-family:Georgia,serif">
      <div style="max-width:580px;margin:32px auto;background:#0d1f1d;border:1px solid #285A48;border-radius:16px;overflow:hidden">
        <div style="background:linear-gradient(135deg,#7f1d1d,#991b1b);padding:32px;text-align:center">
          <h1 style="margin:0;color:#fecaca;font-size:26px">ShopSphere</h1>
          <p style="margin:6px 0 0;color:#fee2e2;font-size:13px">Order Cancellation</p>
        </div>
        <div style="padding:32px">
          <h2 style="color:#fca5a5;margin:0 0 12px;font-size:20px">Order #{order_id} Cancelled</h2>
          <p style="color:#B0E4CC;font-size:14px;line-height:1.6;margin:0 0 20px">
            Your order has been successfully cancelled.
            A refund of <strong style="color:#5DF8D8">₹{total:,.2f}</strong>
            will be processed to your original payment method within 5-7 business days.
          </p>
          <div style="background:#1e4435;border-radius:10px;padding:14px 16px;margin-bottom:24px">
            <p style="color:#B0E4CC;margin:0;font-size:13px">
              If you did not request this cancellation or have any questions,
              please contact our support team immediately.
            </p>
          </div>
          <a href="http://localhost/products"
             style="display:inline-block;background:#408A71;color:#091413;padding:12px 24px;border-radius:10px;text-decoration:none;font-weight:bold;font-size:14px">
            Continue Shopping
          </a>
        </div>
        <div style="background:#091413;padding:20px;text-align:center;border-top:1px solid #285A48">
          <p style="color:#285A48;font-size:12px;margin:0">
            © {datetime.now().year} ShopSphere · Automated email, please do not reply.
          </p>
        </div>
      </div>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Order #{order_id} Cancelled — Refund Initiated"
        msg["From"]    = f"ShopSphere <{EMAIL_ADDRESS}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
        print(f"[notify] Cancellation email sent to {to_email} for order #{order_id}")
    except Exception as e:
        print(f"[notify] Cancellation email error: {e}")
        
# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    connection = None
    for attempt in range(15):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host="rabbitmq")
            )
            break
        except Exception:
            print(f"[notify] Waiting for RabbitMQ... ({attempt + 1}/15)")
            time.sleep(3)

    if not connection:
        print("[notify] Could not connect to RabbitMQ — exiting")
        return

    channel = connection.channel()
    channel.queue_declare(queue="order_created",   durable=True)
    channel.queue_declare(queue="order_cancelled", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="order_created",   on_message_callback=on_order_created)
    channel.basic_consume(queue="order_cancelled", on_message_callback=on_order_cancelled)
    print(f"[notify] Listening... (email: {EMAIL_ADDRESS or 'NOT SET'})")
    channel.start_consuming()


if __name__ == "__main__":
    main()
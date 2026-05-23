import pika, time

_conn = None
_ch   = None


def get_channel():
    global _conn, _ch
    try:
        if _conn and _conn.is_open:
            return _ch
    except Exception:
        pass

    for _ in range(10):
        try:
            _conn = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
            _ch   = _conn.channel()
            _ch.queue_declare(queue="order_created", durable=True)
            _ch.queue_declare(queue="order_cancelled", durable=True)
            return _ch
        except Exception:
            time.sleep(3)

    return None

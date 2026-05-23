FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run consumer (background) + API server (foreground) in one container.
# consumer.py listens on RabbitMQ for order events and decrements stock.
CMD sh -c "python consumer.py & uvicorn main:app --host 0.0.0.0 --port 8000"

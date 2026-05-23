FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run Django migrations then start gunicorn
CMD sh -c "python manage.py migrate --noinput && \
           gunicorn order_service.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120"

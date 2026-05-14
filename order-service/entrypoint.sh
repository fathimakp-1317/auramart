#!/bin/bash

echo "======================================"
echo "  ShopSphere Order Service Starting"
echo "======================================"

echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST ${DB_PORT:-5432}; do
    sleep 1
    echo "Still waiting for PostgreSQL..."
done
echo "PostgreSQL is ready!"

echo "Waiting for Redis..."
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
    sleep 1
    echo "Still waiting for Redis..."
done
echo "Redis is ready!"

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Django server..."
python manage.py runserver 0.0.0.0:5003
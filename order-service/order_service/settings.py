import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY   = os.getenv("DJANGO_SECRET_KEY", "django-insecure-change-me-in-production")
DEBUG        = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "orders",
]

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "order_service.urls"

DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends.postgresql",
        "NAME":     os.getenv("DB_NAME",     "shopsphere"),
        "USER":     os.getenv("DB_USER",     "admin"),
        "PASSWORD": os.getenv("DB_PASSWORD", "admin"),
        "HOST":     os.getenv("DB_HOST",     "postgres"),
        "PORT":     os.getenv("DB_PORT",     "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES":   ["rest_framework.parsers.JSONParser"],
}

# Service config read from env
PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8000")
JWT_SECRET          = os.getenv("JWT_SECRET", "change-me-before-deploy")
STRIPE_SECRET_KEY   = os.getenv("STRIPE_SECRET_KEY", "")

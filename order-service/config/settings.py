import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-change-this"
)

DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS", "*"
).split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "apps.orders",
    "apps.cart",
    "apps.payments",
    "apps.inventory",
    "django_extensions",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends"
            ".django.DjangoTemplates"
        ),
        "DIRS": [
            BASE_DIR / "templates"
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ─── Database ─────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME":     os.getenv(
                "DB_NAME", "shopsphere_orders"
            ),
            "USER":     os.getenv(
                "DB_USER", "postgres"
            ),
            "PASSWORD": os.getenv(
                "DB_PASSWORD", "password"
            ),
            "HOST":     os.getenv(
                "DB_HOST", "localhost"
            ),
            "PORT":     os.getenv(
                "DB_PORT", "5432"
            ),
        }
    }

REDIS_URL    = os.getenv(
    "REDIS_URL", "redis://localhost:6379"
)
STRIPE_KEY   = os.getenv("STRIPE_SECRET_KEY")
RABBITMQ_URL = os.getenv("RABBITMQ_URL")

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ─── Celery Settings ──────────────────────────
CELERY_BROKER_URL = os.getenv(
    "REDIS_URL", "redis://localhost:6379"
)
CELERY_RESULT_BACKEND = os.getenv(
    "REDIS_URL", "redis://localhost:6379"
)
CELERY_ACCEPT_CONTENT    = ["json"]
CELERY_TASK_SERIALIZER   = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE          = "UTC"
CELERY_TASK_MAX_RETRIES  = 3
CELERY_TASK_RETRY_DELAY  = 60
CELERY_RESULT_EXTENDED   = True

INSTALLED_APPS += [
    "django_celery_results",
    "django_celery_beat",
]

# ─── Email Settings ───────────────────────────
EMAIL_BACKEND = (
    "django.core.mail.backends"
    ".console.EmailBackend"
)
EMAIL_HOST = os.getenv(
    "EMAIL_HOST", "smtp.gmail.com"
)
EMAIL_PORT = int(os.getenv(
    "EMAIL_PORT", "587"
))
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.getenv(
    "EMAIL_HOST_USER", ""
)
EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD", ""
)
DEFAULT_FROM_EMAIL  = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "noreply@shopsphere.com"
)
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000"
)

# ─── Static Files ─────────────────────────────
STATIC_URL       = "/static/"
STATIC_ROOT      = os.path.join(
    BASE_DIR, "staticfiles"
)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend")
]

DEFAULT_CHARSET = "utf-8"
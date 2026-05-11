"""
Test Settings
=============
Separate settings for running tests.
Uses SQLite instead of PostgreSQL
so tests run faster without needing
a real database.
"""

from .settings import *

# use SQLite for tests
# faster and no setup needed
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":   ":memory:",
        # :memory: means database lives in RAM
        # deleted after tests finish
    }
}

# use faster password hasher for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# disable email sending in tests
EMAIL_BACKEND = (
    "django.core.mail.backends.locmem.EmailBackend"
)

# use local memory cache for tests
CACHES = {
    "default": {
        "BACKEND": (
            "django.core.cache.backends"
            ".locmem.LocMemCache"
        )
    }
}
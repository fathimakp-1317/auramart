"""
Celery Configuration
====================
This sets up Celery for our Django project.
Celery runs background tasks without
blocking the main API.

We use Redis as the broker
(message queue between Django and Celery)
"""

import os
from celery import Celery
from django.conf import settings

# tell Celery which settings to use
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

# create Celery app
app = Celery("order_service")

# load config from Django settings
# all Celery settings start with CELERY_
app.config_from_object(
    "django.conf:settings",
    namespace="CELERY"
)

# auto-discover tasks in all installed apps
# looks for tasks.py in each app
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    """
    Simple test task.
    Run this to confirm Celery is working.
    """
    print(f"Request: {self.request!r}")
    return "Celery is working!"
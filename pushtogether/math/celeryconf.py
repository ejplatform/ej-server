import os

from celery import Celery  
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery('pushtogether.math')

CELERY_TIMEZONE = 'UTC'

app.config_from_object('django.conf:settings')  
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

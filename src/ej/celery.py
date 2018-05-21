import os
from logging import getLogger

from django.conf import settings

log = getLogger('celery')

try:
    from celery import Celery
except ImportError:
    log.info('celery not loaded')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ej.settings')
    app = Celery('ej')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
    log.info('celery started')

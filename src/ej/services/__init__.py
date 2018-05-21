from django.conf import settings
from . import redis


if settings.DB == 'postgres':
    from . import postgres
    postgres.start_postgres()


import logging

SERVICES_STARTED = False

log = logging.getLogger('ej')


def start_services(settings):
    global SERVICES_STARTED

    if SERVICES_STARTED:
        return

    engine = settings.DATABASES['default']['ENGINE']
    log.debug(f'database engine: {engine}')

    if engine == 'django.db.backends.postgresql':
        from . import postgres
        postgres.start_postgres()

    SERVICES_STARTED = True

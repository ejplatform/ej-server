import logging

log = logging.getLogger('ej')
SERVICES_STARTED = False


def start_services(settings):
    global SERVICES_STARTED

    if SERVICES_STARTED:
        return

    print('waiting for services to start')

    if 'pgsql' in settings.DATABASES['default']['ENGINE']:
        from . import postgres
        postgres.start_postgres()

    SERVICES_STARTED = True

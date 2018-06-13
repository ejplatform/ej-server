SERVICES_STARTED = False


def start_services(settings):
    global SERVICES_STARTED

    if SERVICES_STARTED:
        return

    print('waiting for services to start')

    if 'django.db.backends.postgresql_psycopg2' == \
        settings.DATABASES['default']['ENGINE']:

        print('waiting for postgres to start')
        from . import postgres
        postgres.start_postgres()

    SERVICES_STARTED = True

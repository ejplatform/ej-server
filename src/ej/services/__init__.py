SERVICES_STARTED = False


def start_services(settings):
    global SERVICES_STARTED

    if SERVICES_STARTED:
        return

    print('Waiting for services to start')
    print('Current database backend: '
          f'{settings.DATABASES["default"]["ENGINE"]}')

    if 'django.db.backends.postgresql' == \
        settings.DATABASES['default']['ENGINE']:

        print('waiting for postgres to start')
        from . import postgres
        postgres.start_postgres()

    SERVICES_STARTED = True

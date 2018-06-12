import importlib
import os
import time
import logging
log = logging.getLogger('ej')

def start_postgres():
    settings_path = os.environ['DJANGO_SETTINGS_MODULE']
    settings = importlib.import_module(settings_path)

    db = settings.DATABASE['default']
    dbname = db['DBNAME']
    user = db['USER']
    password = db['PASSWORD']
    host = db['HOST']

    for _ in range(100):
        if can_connect(dbname, user, password, host):
            log.info("Postgres is available. Continuing...")
            return
        log.warn('Postgres is unavailable. Retrying in 0.5 seconds')
        time.sleep(0.5)
    raise SystemExit('Maximum number of attempts connecting to postgres database')


def can_connect(dbname, user, password, host):
    import psycopg2

    try:
        psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host
        )
    except psycopg2.OperationalError:
        return False
    return True

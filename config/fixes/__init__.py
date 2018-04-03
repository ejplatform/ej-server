import logging

from . import django_old_apis

log = logging.getLogger('ej-fixes')

fixes = [django_old_apis.fix]


def apply_all():
    for fix in fixes:
        log.info('monkey patch: ' + fix.__doc__.strip())
        fix()

import logging

log = logging.getLogger('ej-fixes')


def apply_all():
    from . import django_old_apis
    from . import sidekick

    fixes = [django_old_apis.fix, sidekick.fix]  # , pinax_points.fix]

    for fix in fixes:
        log.info('monkey patch: ' + fix.__doc__.strip())
        fix()

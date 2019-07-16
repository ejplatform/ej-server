import logging

from django.core.exceptions import ImproperlyConfigured


def apply_all():
    # from . import django_old_apis
    from . import sidekick

    fixes = [
        # django_old_apis.fix,
        # pinax_points.fix,
        sidekick.fix,
    ]

    try:
        log = logging.getLogger("ej-fixes").info
    except ImproperlyConfigured:
        log = print

    for fix in fixes:
        log("monkey patch: " + fix.__doc__.strip())
        fix()

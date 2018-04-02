#
# This fix inject old Django APIs on new Django.
#
import sys
import logging

log = logging.getLogger('ej-fixes')

def fix():
    """
    Monkey patch parts of Django to make old apps still work.
    """

    from django import urls
    from django.utils import functional

    # Used by Django Activity Stream and Django Autoslug
    sys.modules['django.core.urlresolvers'] = urls
    log.info('django-activity-stream requires monkey patching to work on Django 2.0')
    log.info('django-autoslug requires monkey patching to work on Django 2.0')

    # Crispy forms use allow_lazy instead of keep_lazy.
    functional.allow_lazy = functional.keep_lazy
    log.info('django-crispy-forms requires monkey patching to work on Django 2.0')


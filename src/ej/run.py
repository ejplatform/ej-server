import os

from django import setup as _setup


def start(settings="ej.settings"):
    """
    Start Django based on the given settings module.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
    _setup()

    from django.conf import settings

    settings.ALLOWED_HOSTS.append("testserver")


def run(func, *args, **kwargs):
    """
    Starts Django and run function with the remaining arguments.
    """
    start()
    func(*args, **kwargs)

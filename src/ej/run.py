import os
from django import setup


def start(settings="ej.settings"):
    """
    Start Django based on the given settings module.
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
    setup()


def run(func, *args, **kwargs):
    """
    Starts Django and run function with the remaining arguments.
    """
    start()
    func(*args, **kwargs)

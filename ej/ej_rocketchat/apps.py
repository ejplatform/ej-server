from django.apps import AppConfig


class EJRocketchatConfig(AppConfig):
    name = 'ej.ej_rocketchat'

    def ready(self):
        from . import signals  # noqa

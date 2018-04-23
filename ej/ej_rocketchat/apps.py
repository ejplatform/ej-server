from django.apps import AppConfig


class EJRocketchatConfig(AppConfig):
    name = 'ej_rocketchat'

    def ready(self):
        from . import signals  # noqa

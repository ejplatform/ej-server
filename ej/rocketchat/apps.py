from django.apps import AppConfig


class RocketchatConfig(AppConfig):
    name = 'rocketchat'

    def ready(self):
        from . import signals  # noqa

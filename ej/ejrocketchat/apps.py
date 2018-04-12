from django.apps import AppConfig


class EJRocketChatConfig(AppConfig):
    name = 'ej.rocketchat'

    def ready(self):
        from . import signals  # noqa

from django.apps import AppConfig


class EJRocketChatConfig(AppConfig):
    name = 'ejrocketchat'

    def ready(self):
        from . import signals  # noqa

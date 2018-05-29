from django.apps import AppConfig


class EJRocketchatConfig(AppConfig):
    name = 'ej_rocketchat'
    signals = None

    def ready(self):
        from . import signals

        self.signals = signals

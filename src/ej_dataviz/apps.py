from django.apps import AppConfig


class EjDatavizConfig(AppConfig):
    name = 'ej_dataviz'

    def ready(self):
        from . import roles
        self.roles = roles

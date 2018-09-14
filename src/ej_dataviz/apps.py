from django.apps import AppConfig


class EjDatavizConfig(AppConfig):
    name = 'ej_dataviz'
    roles = None

    def ready(self):
        from . import roles
        self.roles = roles

from django.apps import AppConfig


class EjProfilesConfig(AppConfig):
    name = 'ej_profiles'

    def ready(self):
        from . import rules
        self.rules = rules

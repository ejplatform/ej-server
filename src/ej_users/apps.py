from django.apps import AppConfig


class EjUsersConfig(AppConfig):
    name = 'ej_users'
    verbose_name = "Users"

    def ready(self):
        from .rules import rules
        self.rules = rules

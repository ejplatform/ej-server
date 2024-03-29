from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EjUsersConfig(AppConfig):
    name = "ej_users"
    verbose_name = _("Users")

    def ready(self):
        import ej_users.signals

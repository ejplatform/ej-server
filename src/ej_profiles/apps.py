from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EjProfilesConfig(AppConfig):
    name = "ej_profiles"
    verbose_name = _("Profiles")

    api = None

    def ready(self):
        from . import api

        self.api = api

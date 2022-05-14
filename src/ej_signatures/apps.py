from django.apps import AppConfig
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class EjSignaturesConfig(AppConfig):
    name = "ej_signatures"
    verbose_name = _("Signatures")
    rules = None
    api = None
    roles = None

    def ready(self):
        pass
        # from . import rules, api, roles

        # self.rules = rules
        # self.api = api
        # self.roles = roles

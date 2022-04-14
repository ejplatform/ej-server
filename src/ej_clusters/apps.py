from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EjClustersConfig(AppConfig):
    name = "ej_clusters"
    verbose_name = _("Clusters")
    rules = None
    api = None

    def ready(self):
        from . import rules
        from . import api

        self.rules = rules
        self.api = api

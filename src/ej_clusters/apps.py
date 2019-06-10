from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EjClustersConfig(AppConfig):
    name = "ej_clusters"
    verbose_name = _("Clusters")
    rules = None
    signals = None
    api = None

    def ready(self):
        from . import rules
        from . import signals
        from . import api

        self.rules = rules
        self.signals = signals
        self.api = api

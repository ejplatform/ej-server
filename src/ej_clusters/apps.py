from django.apps import AppConfig


class EjClustersConfig(AppConfig):
    name = 'ej_clusters'

    def ready(self):
        from . import rules

        self.rules = rules

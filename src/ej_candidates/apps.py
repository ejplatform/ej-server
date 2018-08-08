from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class CandidatesConfig(AppConfig):
    name = 'ej_candidates'
    verbose_name = _('Candidates')
    api = None

    def ready(self):
        from . import api
        self.api = api

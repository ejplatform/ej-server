from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from boogie.rest import rest_api

from .filters import *

class CandidatesConfig(AppConfig):
    name = 'ej_candidates'
    verbose_name = _('Candidates')
    api = None

    def ready(self):
        from . import api
        from ej_candidates.models.candidate import Candidate
        # overwrite boogie viewset, and use besouro implementation.
        # This is necessary to filter candidates for unlogged users.
        def get_queryset(self):
            try:
                limit = int(request.GET.get("limit"))
            except:
                limit = 10
            querySet = Candidate.objects.all()
            filters = get_filters(self.request.GET)
            if (valid_filters(filters)):
                result = filter_candidates(querySet, filters);
                if (result):
                    return result.order_by("-id")[:limit]
                else:
                    return []
            else:
                # order_by('?') randomize the querySet result.
                # This is not the best aproach, but
                # 9000 candidates are few data to retrieve.
                return querySet.order_by('?')[:limit]
        self.api = api
        rest_api_v1 = rest_api.get_api_info('v1')
        candidate_view_set = rest_api_v1.viewset_class(Candidate)
        candidate_view_set.get_queryset = get_queryset


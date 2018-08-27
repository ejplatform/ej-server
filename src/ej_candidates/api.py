from boogie.rest import rest_api
from django.http import JsonResponse
import json

from .models.candidate import Candidate
from .models.selected_candidates import SelectedCandidate
from .filters import *

@rest_api.action('ej_users.User')
def candidates(request, user):
    limit = get_query_limit(request)
    querySet = Candidate.objects.exclude(selectedcandidate__user_id=user.id)\
        .exclude(pressedcandidate__user_id=user.id)\
        .exclude(ignoredcandidate__user_id=user.id)
    filters = get_filters(request.GET)
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

@rest_api.action('ej_users.User')
def selected_candidates(request, user):
    limit = get_query_limit(request)
    querySet = Candidate.objects.filter(selectedcandidate__user_id=user.id)
    filters = get_filters(request.GET)
    if (valid_filters(filters)):
        result = filter_candidates(querySet, filters);
        if (result):
            return result.order_by("-id")[:limit]
        else:
            return []
    else:
        return querySet.order_by("-id")[:limit]

@rest_api.action('ej_users.User')
def total_selected_candidates(request, user):
    querySet = Candidate.objects.filter(selectedcandidate__user_id=user.id).count()
    return {'total': querySet}

@rest_api.action('ej_users.User', methods=['post'])
def unselect_candidate(request, user):
    candidate = json.loads(request.body.decode("utf8"))["candidate"]
    SelectedCandidate.objects.get(candidate=candidate, user=user).delete()

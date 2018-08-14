from boogie.rest import rest_api
import json

from .models.candidate import Candidate
from .models.selected_candidates import SelectedCandidate
#
# User extra actions and attributes
#

def filter_by_name(querySet, filter):
    return querySet.filter(name=filter.upper())

def filter_candidates(querySet, filter):
        return filter_by_name(querySet, filter)

@rest_api.action('ej_users.User')
def candidates(request, user):
    querySet = Candidate.objects.exclude(selectedcandidate__user_id=user.id)\
        .exclude(pressedcandidate__user_id=user.id)
    filter = request.GET.get('filter_by_name')
    if (filter):
        return filter_candidates(querySet, filter)
    else:
        return querySet.order_by("-id")[:10]

@rest_api.action('ej_users.User')
def selected_candidates(request, user):
    return Candidate.objects.filter(selectedcandidate__user_id=user.id)

@rest_api.action('ej_users.User', methods=['post'])
def unselect_candidate(request, user):
    candidate = json.loads(request.body.decode("utf8"))["candidate"]
    SelectedCandidate.objects.get(candidate=candidate, user=user).delete()

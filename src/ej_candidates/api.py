from boogie.rest import rest_api
import json

from .models.candidate import Candidate
from .models.selected_candidates import SelectedCandidate
#
# User extra actions and attributes
#

def filter_by_name(querySet, filter):
    if(querySet):
        filteredCandidates = querySet.filter(name__contains=filter.upper())
        if(filteredCandidates):
            return filteredCandidates
        return []

def filter_by_party(querySet, filter):
    if(querySet):
        filteredCandidates = querySet.filter(party=filter.upper())
        if(filteredCandidates):
            return filteredCandidates
        return []

def filter_by_candidacy(querySet, filter):
    if(querySet):
        filteredCandidates = querySet.filter(candidacy=filter.upper())
        if(filteredCandidates):
            return filteredCandidates
        return []

def filter_by_uf(querySet, filter):
    if(querySet):
        filteredCandidates = querySet.filter(uf=filter.upper())
        if(filteredCandidates):
            return filteredCandidates
        return []


def filter_candidates(querySet, filters):
    if(filters["filter_by_uf"]):
        querySet = filter_by_uf(querySet, filters["filter_by_uf"])
    if(filters["filter_by_name"]):
        querySet = filter_by_name(querySet, filters["filter_by_name"])
    if(filters["filter_by_party"]):
        querySet = filter_by_party(querySet, filters["filter_by_party"])
    if(filters["filter_by_candidacy"]):
        querySet = filter_by_candidacy(querySet, filters["filter_by_candidacy"])
    return querySet

def get_filters(request):
    filters = {}
    filters["filter_by_name"] = request.get('filter_by_name')
    filters["filter_by_uf"] = request.get('filter_by_uf')
    filters["filter_by_party"] = request.get('filter_by_party')
    filters["filter_by_candidacy"] = request.get('filter_by_candidacy')
    return filters

def valid_filters(filters):
    return filters["filter_by_name"] or filters["filter_by_uf"] or\
        filters["filter_by_party"] or filters["filter_by_candidacy"]

@rest_api.action('ej_users.User')
def candidates(request, user):
    querySet = Candidate.objects.exclude(selectedcandidate__user_id=user.id)\
        .exclude(pressedcandidate__user_id=user.id)\
        .exclude(ignoredcandidate__user_id=user.id)
    filters = get_filters(request.GET)
    if (valid_filters(filters)):
        return filter_candidates(querySet, filters)
    else:
        limit = int(request.GET.get("limit"))
        return querySet.order_by("-id")[:limit]

@rest_api.action('ej_users.User')
def selected_candidates(request, user):
    querySet = Candidate.objects.filter(selectedcandidate__user_id=user.id)
    filters = get_filters(request.GET)
    if (valid_filters(filters)):
        return filter_candidates(querySet, filters)
    else:
        limit = int(request.GET.get("limit"))
        return querySet.order_by("-id")[:limit]

@rest_api.action('ej_users.User', methods=['post'])
def unselect_candidate(request, user):
    candidate = json.loads(request.body.decode("utf8"))["candidate"]
    SelectedCandidate.objects.get(candidate=candidate, user=user).delete()

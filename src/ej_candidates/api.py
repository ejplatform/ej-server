from boogie.rest import rest_api
from .models.candidate import Candidate
from .models.selected_candidates import SelectedCandidate

#
# User extra actions and attributes
#

@rest_api.action('ej_users.User')
def candidates(request, user):
    return Candidate.objects.exclude(selectedcandidate__user_id=user.id)

# boogie has a bug. The underscore from the decorated method
# is not being replaced by a an hifen.Fabio will fix it.
@rest_api.action('ej_users.User')
def selected_candidates(request, user):
    return Candidate.objects.filter(selectedcandidate__user_id=user.id)

@rest_api.action('ej_users.User')
def required_trophies(request, user):
    # Use trophy key or id to return required trophies list.
    key = request.query_params.get('trophy')
    try:
        return Trophy.objects.get(pk=key).required_trophies.all()
    except ValueError:
        return Trophy.objects.get(key=key).required_trophies.all()

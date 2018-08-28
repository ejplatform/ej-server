from boogie.rest import rest_api
from ej_users.models import User
from ej_trophies.models import Trophy
from ej_candidates.models.candidate import Candidate
from ej_candidates.models.selected_candidates import SelectedCandidate

#
# User extra actions and attributes
#

@rest_api.action('ej_users.User')
def profile(request, user):
    return User.get_profile(user)

@rest_api.action('ej_users.User')
def required_trophies(request, user):
    # Use trophy key or id to return required trophies list.
    key = request.query_params.get('trophy')
    try:
        return Trophy.objects.get(pk=key).required_trophies.all()
    except ValueError:
        return Trophy.objects.get(key=key).required_trophies.all()

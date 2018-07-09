from boogie.rest import rest_api
from ej_users.models import User
from .models import UserTrophy
from .models import Trophy

#
# Trophy extra actions and attributes
#
@rest_api.action('ej_users.User')
def trophies(request, user):
    UserTrophy.sync_available_trophies_with_user(user)
    key = request.query_params.get('trophy')
    if key:
        return UserTrophy.get_user_trophy(user, key)
    return UserTrophy.get_user_trophies(user)

@rest_api.action('ej_users.User')
def required_trophies(request, user):
    key = request.query_params.get('trophy')
    return Trophy.objects.get(pk=key).required_trophies.all()

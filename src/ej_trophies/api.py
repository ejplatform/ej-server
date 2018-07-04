from boogie.rest import rest_api
from ej_users.models import User
from .models import UserTrophy

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

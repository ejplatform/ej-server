from boogie.rest import rest_api
from ej_users.models import User

#
# User extra actions and attributes
#

@rest_api.action('ej_users.User')
def profile(request, user):
    return User.get_profile(user)

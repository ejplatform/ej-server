from boogie.rest import rest_api
from rest_framework.response import Response

from .models import Profile


@rest_api.list_action("ej_profiles.Profile")
def phone_number(request):
    if request.user.is_authenticated:
        my_profile = Profile.objects.get(user=request.user).phone_number
        return my_profile
    else:
        return Response(status=403)

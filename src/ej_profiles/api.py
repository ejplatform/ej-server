from boogie.rest import rest_api
from ej_clusters.math import get_raw_votes
from ej_profiles.models import Setting

@rest_api.action('ej_profiles.Profile')
def profile_settings(request, profile):
    return Setting.objects.get(profile=profile)
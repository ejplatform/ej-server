"""Utils methods for ej_profiles app."""
from geopy.geocoders import Nominatim


def get_geoloc(coord):
    """
    Method responsible for requesting geolocation from a given ip.
    """
    geolocator = Nominatim(user_agent='ej_server')
    return geolocator.reverse(coord)

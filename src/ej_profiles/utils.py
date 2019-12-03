import geocoder

from django.utils import timezone


def years_from(date, now=None):
    now = now or timezone.now()
    years = now.year - date.year
    if date.month > now.month or (date.month == now.month and date.day > now.day):
        return years - 1
    return years


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_loc(ip_adr):
    """
    Method to get a lat and log from an ip
    """
    location = geocoder.ip(ip_adr)

    return(location)

from django.conf import settings
from functools import wraps


def custom_headers(func):
    """
    Decorator that adds Access-Control-Allow-Credentials and
    Content-Security-Policy headers to a view function

    Args:
        func (callable):
            A view function to be decorated with the headers
    """

    @wraps(func)
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        res['Access-Control-Allow-Credentials'] = 'true'
        res['Content-Security-Policy'] = \
            'frame-ancestors ' + (' '.join(settings.CSRF_TRUSTED_ORIGINS))
        return res

    return wrap

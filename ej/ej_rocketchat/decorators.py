from constance import config
from django.conf import settings

def custom_headers(func):
    """
    Decorator that adds Access-Control-Allow-Credentials and
    Content-Security-Policy headers to a view function

    Args:
        func (callable):
            A view function to be decorated with the headers
    """
    def wrap(*args, **kwargs):
        res = func(*args, **kwargs)
        res['Access-Control-Allow-Credentials'] = 'true'
        res['Content-Security-Policy'] = \
        'frame-ancestors ' + (' '.join(settings.CORS_ORIGIN_WHITELIST))
        return res
    return wrap

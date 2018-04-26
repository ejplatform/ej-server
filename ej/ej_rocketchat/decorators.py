from constance import config
from django.conf import settings

def allow_credentials(f):
    def wrap(*args, **kwargs):
        res = f(*args, **kwargs)
        res['Access-Control-Allow-Credentials'] = 'true'
        res['Content-Security-Policy'] = \
        'frame-ancestors ' + (' '.join(settings.CORS_ORIGIN_WHITELIST))
        return res
    return wrap

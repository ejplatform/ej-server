def allow_credentials(f):
    def wrap(*args, **kwargs):
        res = f(*args, **kwargs)
        res['Access-Control-Allow-Credentials'] = 'true'
        return res
    return wrap

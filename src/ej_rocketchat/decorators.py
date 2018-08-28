from django.conf import settings
from functools import wraps

from django.http import Http404, HttpResponseServerError
from django.shortcuts import redirect

from .models import CAN_LOGIN_PERM
from .rocket import rocket


def security_policy(func):
    """
    Decorator that adds Access-Control-Allow-Credentials and
    Content-Security-Policy headers to a view function

    Args:
        func (callable):
            A view function to be decorated with the headers
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        response = func(*args, **kwargs)
        policy = ' '.join(['frame-ancestors', *settings.CSRF_TRUSTED_ORIGINS])
        response['Access-Control-Allow-Credentials'] = 'true'
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        response['Content-Security-Policy'] = policy
        return response

    return wrapped


def requires_rc_perm(func):
    """
    Decorator that marks a view that requires an explicit Rocket.Chat login
    permission.
    """

    @wraps(func)
    def decorated(request, *args, **kwargs):
        user = request.user
        if not user.id or not user.has_perm(CAN_LOGIN_PERM):
            raise Http404

        # Try to build the initial context
        if not rocket.has_config:
            if user.is_superuser:
                return redirect('rocket:config')
            else:
                return HttpResponseServerError('invalid-rc-config')
        return func(request, *args, **kwargs)

    return decorated

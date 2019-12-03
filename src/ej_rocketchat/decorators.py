from functools import wraps

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponseServerError
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from .models import CAN_LOGIN_PERM
from .rocket import new_config


def security_policy(func):
    """
    Decorator that adds Access-Control-Allow-Credentials and
    Content-Security-Policy headers to a view function

    Args:
        func (callable):
            A view function to be decorated with the headers
    """

    @wraps(func)
    @csrf_exempt
    def wrapped(*args, **kwargs):
        response = func(*args, **kwargs)
        return with_headers(response)

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
        """
        Try to build the initial context
        """
        if not new_config().has_config:
            if user.is_superuser:
                return redirect("rocket:config")
            else:
                return HttpResponseServerError("invalid-rc-config")
        return func(request, *args, **kwargs)

    return decorated


def get_rocket_url():
    try:
        return new_config().url
    except ImproperlyConfigured:
        return settings.EJ_ROCKETCHAT_URL or "http://localhost:3000"


def with_headers(response):
    frame_ancestors = getattr(settings, "CONTENT_SECURITY_POLICY_FRAME_ANCESTORS", [])
    frame_ancestors = " ".join(["frame-ancestors", *settings.CSRF_TRUSTED_ORIGINS, *frame_ancestors])

    """
    Get header configurations. We try to infer good values from rocket-chat
    configuration. Those headers, however, can be configured to an specific
    value on a per deployment basis
    """
    ac_origin = settings.HTTP_ACCESS_CONTROL_ALLOW_ORIGIN or get_rocket_url()
    ac_credentials = settings.HTTP_ACCESS_CONTROL_ALLOW_CREDENTIALS or "true"
    csp = settings.HTTP_CONTENT_SECURITY_POLICY or frame_ancestors
    xframe_options = settings.HTTP_X_FRAME_OPTIONS or f"allow-from {get_rocket_url()}"
    """
    Save content headers
    """
    response["Access-Control-Allow-Credentials"] = ac_credentials
    response["Access-Control-Allow-Origin"] = ac_origin
    response["Content-Security-Policy"] = csp
    response["X-Frame-Options"] = xframe_options
    return response

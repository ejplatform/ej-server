from concurrent.futures import ThreadPoolExecutor
from logging import getLogger

from django.conf import settings
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from .rocket import rocket

log = getLogger("ej")
executor = ThreadPoolExecutor(max_workers=2)
submit = lambda f, *args: f(*args)
ROCKETCHAT_PERM = "ej_rocketchat.can_login_rocketchat"


#
# Register event handlers if rocketchat integration is enabled
#
def logout_handler(sender, user, request, **kwargs):
    """
    Logout Rocketchat user when receives a Django logout signal.
    """
    # Superuser cannot logout because that would invalidate the Auth token
    if user and not user.is_superuser:
        submit(silence_exceptions(rocket.logout), user)


def silence_exceptions(func):
    """
    Log errors instead of proagating exceptions.
    """

    # noinspection PyBroadException
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            msg = f"Error encountered executing {func.__name__}: {exc}"
            log.error(msg)

    return wrapped


if settings.EJ_ROCKETCHAT_INTEGRATION:
    receiver(user_logged_out)(logout_handler)

from logging import getLogger

from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from .rocket import new_config

log = getLogger("ej")
submit = lambda f, *args: f(*args)


#
# Register event handlers if rocketchat integration is enabled
#
@receiver(user_logged_out)
def logout_handler(sender, user, request, **kwargs):
    """
    Logout Rocketchat user when receives a Django logout signal.
    """
    rocket = new_config()
    try:
        rocket.logout(user)
        log.info("[rocket.logout-handler] Logged {user} from Rocket.chat")
    except Exception as exc:
        msg = f"[rocket.logout-handler] Error during logout: {exc}"
        log.error(msg)

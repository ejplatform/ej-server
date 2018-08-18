from constance import config
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.dispatch import receiver

from . import helpers


@receiver(user_logged_out)
def logout(sender, user, request, **kwargs):
    """
    Logout Rocketchat user when receives a Django logout signal.
    """
    if user and config.EJ_USE_ROCKETCHAT:
        helpers.invalidate_rc_user_token(user)


@receiver(user_logged_in)
def login(sender, user, request, **kwargs):
    """
    Login Rocketchat user when receives a Django login signal.
    """
    if config.EJ_USE_ROCKETCHAT:
        pass

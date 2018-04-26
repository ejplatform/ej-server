from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from constance import config

from . import helpers


@receiver(user_logged_out)
def logout(sender, user, request, **kwargs):
    """
    Logout Rocketchat user when receives a Django logout signal.
    """
    if user and config.ROCKETCHAT_URL:
        helpers.invalidade_rc_user_token(user.username)

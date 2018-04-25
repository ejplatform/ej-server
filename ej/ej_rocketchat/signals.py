from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from constance import config

from . import helpers


@receiver(user_logged_out)
def logout(sender, user, request, **kwargs):
    if user:
        helpers.invalidade_rc_user_token(user.username) 

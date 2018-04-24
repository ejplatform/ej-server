from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from constance import config

from . import helpers


@receiver(user_logged_out)
def logout(sender, user, request, **kwargs):
   helpers.enable_rc_user_login(user.username, False) 

from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

from constance import config


#@receiver(user_logged_out)
def logout(sender, user, request, **kwargs):
    raise 'Not Implemented Yet'

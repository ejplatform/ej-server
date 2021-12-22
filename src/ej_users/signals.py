import logging
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

log = logging.getLogger("ej")
User = get_user_model()


@receiver(user_logged_in)
def create_board_social(sender, user, request, **kwargs):
    User.create_user_default_board(user)
    log.info("board successfully checked")

import logging
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save

log = logging.getLogger("ej")
User = get_user_model()


@receiver(user_logged_in)
def create_board_social(sender, user, request, **kwargs):
    User.create_user_default_board(user)
    log.info("board successfully checked")


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance: User, **kwargs):
    instance.get_profile()
    log.info("profile successfully created")

from datetime import datetime, timedelta
from logging import getLogger
from abc import ABC, abstractmethod
from constance import config

from django.contrib.auth.models import Permission
from boogie.apps.users.models import AbstractUser
from boogie.rest import rest_api
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from .manager import UserManager
from .utils import random_name, token_factory

log = getLogger("ej")


class Signature(ABC):
    """
    Abstract class that defines generic actions to be performed by its signature subclasses.
    """

    def __init__(self, user):
        self.user = user

    def can_add_conversation(self) -> bool:
        if self.user.is_superuser:
            return True

        user_conversations_count = self.user.conversations.count()
        if user_conversations_count < self.get_conversation_limit():
            return True
        else:
            return False

    def can_vote(self) -> bool:
        if self.user.is_superuser:
            return True

        user_vote_count = self.user.votes.count()
        if user_vote_count < self.get_vote_limit():
            return True
        else:
            return False

    @abstractmethod
    def get_conversation_limit(self) -> int:
        pass

    @abstractmethod
    def get_vote_limit(self) -> int:
        pass


class ListenToCommunity(Signature):
    def get_conversation_limit(self) -> int:
        return config.EJ_LISTEN_TO_COMMUNITY_SIGNATURE_CONVERSATIONS_LIMIT

    def get_vote_limit(self) -> int:
        return config.EJ_LISTEN_TO_COMMUNITY_SIGNATURE_VOTE_LIMIT


class ListenToCity(Signature):
    def get_conversation_limit(self) -> int:
        return config.EJ_LISTEN_TO_CITY_SIGNATURE_CONVERSATIONS_LIMIT

    def get_vote_limit(self) -> int:
        return config.EJ_LISTEN_TO_CITY_SIGNATURE_VOTE_LIMIT


class SignatureFactory:
    """
    Instantiates signature subclasses
    Usage:

    signature = SignatureFactory.get_user_signature(request.user)
    signature.<method-from-class>()
    """

    LISTEN_TO_COMMUNITY = "listen_to_community"
    LISTEN_TO_CITY = "listen_to_city"

    signatures = {LISTEN_TO_COMMUNITY: ListenToCommunity, LISTEN_TO_CITY: ListenToCity}

    @staticmethod
    def get_user_signature(user) -> Signature:
        signature = SignatureFactory.signatures.get(user.signature)
        try:
            return signature(user)
        except:
            return None

    @staticmethod
    def plans():
        return [
            (SignatureFactory.LISTEN_TO_COMMUNITY, "Listen to community"),
            (SignatureFactory.LISTEN_TO_CITY, "Listen to city"),
        ]


@rest_api(["id", "display_name", "email", "signature"])
class User(AbstractUser):
    """
    Default user model for EJ platform.
    """

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    email = models.EmailField(_("email address"), unique=True, help_text=_("Your e-mail address"))
    display_name = models.CharField(
        max_length=50, default=random_name, help_text=_("Name used to publicly identify user")
    )
    username = property(lambda self: self.name or self.email.replace("@", "__"))
    signature = models.CharField(
        _("Signature"),
        max_length=50,
        blank=False,
        help_text=_("User signature"),
        choices=SignatureFactory.plans(),
        default=SignatureFactory.LISTEN_TO_COMMUNITY,
    )
    objects = UserManager()

    class Meta:
        swappable = "AUTH_USER_MODEL"

    @staticmethod
    def create_user_default_board(instance):
        from ej_boards.models import Board

        try:
            board_default = Board.objects.get(slug=instance.email)
        except Exception:
            board_default = Board(
                slug=instance.email,
                owner=instance,
                title="My Board",
                description="Default user board",
                palette="brand",
            )
            board_default.save()
        return board_default

    def default_board_url(self):
        from django.utils.text import slugify

        return "/" + slugify(self.email[:50]) + "/conversations"


class PasswordResetToken(TimeStampedModel):
    """
    Expiring token for password recovery.
    """

    url = models.CharField(_("User token"), max_length=50, unique=True, default=token_factory)
    is_used = models.BooleanField(default=False)
    user = models.ForeignKey("User", on_delete=models.CASCADE)

    @property
    def is_expired(self):
        time_now = datetime.now(timezone.utc)
        return (time_now - self.created).total_seconds() > 600

    def use(self, commit=True):
        self.is_used = True
        if commit:
            self.save(update_fields=["is_used"])


def clean_expired_tokens():
    """
    Clean up used and expired tokens.
    """
    threshold = datetime.now(timezone.utc) - timedelta(seconds=600)
    expired = PasswordResetToken.objects.filter(created__lte=threshold)
    used = PasswordResetToken.objects.filter(is_used=True)
    (used | expired).delete()


def remove_account(user):
    """
    Remove user's account:

    * Mark the account as inactive.
    * Remove all information from user profile.
    * Assign a random e-mail.
    * Set user name to Anonymous.

    # TODO:
    * Remove all boards?
    * Remove all conversations created by the user?
    """
    if hasattr(user, "profile"):
        remove_profile(user)

    # Handle user object
    email = user.email
    user.is_active = False
    user.is_superuser = False
    user.is_staff = False
    user.name = _("Anonymous")
    user.save()

    # Remove e-mail overriding django validator
    new_email = f"anonymous-{user.id}@deleted-account"
    User.objects.filter(id=user.id).update(email=new_email)
    log.info(f"{email} removed account")


def remove_profile(user):
    """
    Erase profile information.
    """

    profile = user.profile.__class__(user=user, id=user.profile.id)
    profile.save()


class MetaData(models.Model):
    """
    A model to stores user metadata.
    """

    # gid
    analytics_id = models.CharField(max_length=100, blank=True, null=True)
    # mtc_id
    mautic_id = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

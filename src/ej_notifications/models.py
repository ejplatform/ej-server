from django.db import models
from django.contrib.auth import get_user_model
from boogie.rest import rest_api
from autoslug import AutoSlugField
from django.utils.translation import ugettext_lazy as _
from boogie import IntEnum
from boogie.fields import EnumField

from ej_profiles.models import Profile

User = get_user_model()


class Purpose(IntEnum):
    GENERAL = 0, _('General')
    CONVERSATION = 1, _('Conversation')
    GROUP = 2, _('Group')
    TROPHIES = 3, _('Trophies')
    ADMIN = 4, _('Admin')
    APPROVED_NOTIFICATIONS = 5, _('Approved Notifications')
    DISAPPROVED_NOTIFICATIONS = 6, _('Disapproved Notifications')


class NotificationOptions(IntEnum):
    ENABLED = 0, _('Enabled')
    DISABLED = 1, _('Disabled')
    PUSH_NOTIFICATIONS = 3, _('Push notifications')


@rest_api(
    ['name', 'users', 'owner', 'purpose', 'created_at'],
    lookup_field='slug',
)
class Channel(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, blank=True)
    purpose = EnumField(Purpose, _('Purpose'), default=Purpose.GENERAL)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="channel_owner")
    slug = AutoSlugField(
        unique=True,
        populate_from='name',
    )

    class Meta:
        ordering = ['slug']


class Message(models.Model):
    title = models.CharField(max_length=100)
    body = models.CharField(max_length=250)
    link = models.CharField(max_length=250, blank=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    status = models.CharField(max_length=100, default="pending")
    target = models.IntegerField(blank=True, default=0)

    class Meta:
        ordering = ['title']


class Notification(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
    read = models.BooleanField(default=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)


@rest_api(['id', 'notification_option'])
class NotificationConfig(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='raw_notificationsconfig')
    notification_option = EnumField(NotificationOptions, _('Notification options'), default=NotificationOptions.ENABLED)

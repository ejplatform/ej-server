from django.db import models
from boogie.rest import rest_api
from autoslug import AutoSlugField
from django.utils.translation import ugettext_lazy as _
from boogie import IntEnum
from boogie.fields import EnumField

from ej_users.models import User


class Purpose(IntEnum):
    GENERAL = 0, _('General')
    CONVERSATION = 1, _('Conversation')
    GROUP = 2, _('Group')
    TROPHIES = 3, _('Trophies')
    ADMIN = 4, _('Admin')
    APPROVED_NOTIFICATIONS = 5, _('Approved Notifications')
    DISAPPROVED_NOTIFICATIONS = 6, _('Disapproved Notifications')


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

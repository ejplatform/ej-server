from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel

from boogie import models
from boogie.rest import rest_api
from ej_notifications.enums import Purpose, NotificationMode

User = get_user_model()

# REFS:
#  https://www.digitalocean.com/community/tutorials/how-to-send-web-push-notifications-from-django-applications
#  https://developers.google.com/web/ilt/pwa/introduction-to-push-notifications


@rest_api(["name", "users", "owner", "purpose", "created"], lookup_field="slug")
class Channel(TimeStampedModel):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="channels", blank=True)
    purpose = models.EnumField(Purpose, _("Purpose"), default=Purpose.GENERAL)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name="owned_channels"
    )
    slug = AutoSlugField(unique=True, populate_from="name")

    class Meta:
        ordering = ["slug"]


class Message(TimeStampedModel):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    body = models.CharField(max_length=250)
    link = models.CharField(max_length=250, blank=True)
    status = models.CharField(max_length=100, default="pending")
    target = models.IntegerField(blank=True, default=0)

    class Meta:
        ordering = ["title"]


class Notification(TimeStampedModel):
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="notifications")
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)


@rest_api(["id", "notification_option"])
class NotificationConfig(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_options"
    )
    notification_option = models.EnumField(
        NotificationMode, _("Notification options"), default=NotificationMode.ENABLED
    )

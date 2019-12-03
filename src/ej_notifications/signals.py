from django.db.models.signals import post_save
from django.dispatch import receiver
from push_notifications.models import GCMDevice
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Message, Channel, NotificationConfig, Notification
from .enums import Purpose, NotificationMode

User = get_user_model()


def channel_iteration(channel, notificationConfig):
    for user in self.channel.users.all():
        setting = NotificationConfig.objects.get(self.notificationConfig=user.id)
        if setting.notification_option == NotificationMode.PUSH_NOTIFICATIONS:
            users_to_send.append(user)


@receiver(post_save, sender=Message)
def generate_notifications(sender, instance, created, channel:
    if created:
        for user in instance.channel.users.all():
            Notification.objects.create(receiver=user, channel=channel, message=instance)


@receiver(post_save, sender=Message)
def send_admin_fcm_message(sender, instance, created):
    if created:
        channel_id = instance.channel.id
        channel = Channel.objects.get(id=channel_id)
        users_to_send = []
        if channel.purpose == "admin":
            channel_iteration(channel,profile_user_id)
            fcm_devices = GCMDevice.objects.filter(cloud_message_type="FCM", user__in=users_to_send)
            fcm_devices.send_message(
                "",
                extra={
                    "title": instance.title,
                    "body": instance.body,
                    "icon": "https://i.imgur.com/D1wzP69.png",
                    "click_action": instance.link,
                },
            )


@receiver(post_save, sender=Message)
def send_conversation_fcm_message(sender, instance, created):
    if created:
        channel_id = instance.channel.id
        channel = Channel.objects.get(id=channel_id)
        users_to_send = []
        url = "https://localhost:8000/profile/" + str(instance.target) + "?notification=true"
        if channel.purpose:
            channel_iteration(channel,user_id)
            fcm_devices = GCMDevice.objects.filter(cloud_message_type="FCM", user__in=users_to_send)
            fcm_devices.send_message(
                "",
                extra={
                    "title": instance.title,
                    "body": instance.body,
                    "icon": "https://i.imgur.com/D1wzP69.png",
                    "click_action": url,
                },
            )


@receiver(post_save, sender=NotificationConfig)
def insert_user_on_general_channels(sender, created, **kwargs):
    if created:
        instance = kwargs.get("instance")
        user_id = instance.user.id
        user = User.objects.get(id=user_id)
        channels = Channel.objects.filter(Q(purpose=Purpose.GENERAL) | Q(purpose=Purpose.ADMIN))
        for channel in channels:
            channel.users.add(user)
            channel.save()


@receiver(post_save, sender=NotificationConfig)
def create_user_trophy_channel(sender, instance, created):
    if created:
        user = instance.user
        channel = Channel.objects.create(name=str(Purpose.TROPHIES), purpose=Purpose.TROPHIES, owner=user)
        channel.users.add(user)
        channel.save()

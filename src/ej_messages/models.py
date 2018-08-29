import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from ej_users.models import User
from ej_channels.models import Channel
from push_notifications.models import APNSDevice, GCMDevice
from ej_profiles.models import Setting

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


@receiver(post_save, sender=Message)
def generate_notifications(sender, instance, created, **kwargs):
	if created:
		#avoid circular import
		from ej_notifications.models import Notification
		channel_id = instance.channel.id
		channel = Channel.objects.get(id=channel_id)
		for user in channel.users.all():
			Notification.objects.create(receiver=user, channel=channel, message=instance)

@receiver(post_save, sender=Message)
def send_admin_fcm_message(sender, instance, created, **kwargs):
	if created:
		channel_id = instance.channel.id
		channel = Channel.objects.get(id=channel_id)
		users_to_send = []
		if channel.sort == 'admin':
			for user in channel.users.all():
				setting = Setting.objects.get(owner_id=user.id)
				if (setting.admin_notifications == True):
					users_to_send.append(user)
			fcm_devices = GCMDevice.objects.filter(cloud_message_type="FCM", user__in=users_to_send)
			fcm_devices.send_message("", extra={"title": instance.title, "body": instance.body,
				"icon":"https://i.imgur.com/D1wzP69.png", "click_action": instance.link})

@receiver(post_save, sender=Message)
def send_conversation_fcm_message(sender, instance, created, **kwargs):
	if created:
		channel_id = instance.channel.id
		channel = Channel.objects.get(id=channel_id)
		users_to_send = []
		url = "https://dev.besouro.ejplatform.org/show-mission/" + str(instance.target) + "?notification=true"
		if "conversation" in channel.sort:
			for user in channel.users.all():
				setting = Setting.objects.get(owner_id=user.id)
				if (setting.conversation_notifications == True):
					users_to_send.append(user)
			fcm_devices = GCMDevice.objects.filter(cloud_message_type="FCM", user__in=users_to_send)
			fcm_devices.send_message("", extra={"title": instance.title, "body": instance.body,
				"icon":"https://i.imgur.com/D1wzP69.png", "click_action": url})
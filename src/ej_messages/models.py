import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from ej_users.models import User
from ej_channels.models import Channel

class Message(models.Model):
	title = models.CharField(max_length=100)
	body = models.CharField(max_length=250)
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE, null=True)
	created_at = models.DateTimeField(null=True, auto_now_add=True)
	status = models.CharField(max_length=100, default="pending")

	class Meta:
		ordering = ['title']


@receiver(post_save, sender=Message)
def generate_notifications(sender, instance, **kwargs):
	#avoid circular import
	from ej_notifications.models import Notification
	channel_id = instance.channel.id
	channel = Channel.objects.get(id=channel_id)
	for user in channel.users.all():
		Notification.objects.create(receiver=user, channel=channel, message=instance)
		
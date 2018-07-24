import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from ej_users.models import User
from ej_channels.models import Channel
from ej_messages.models import Message

class Notification(models.Model):
	receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver")
	read = models.BooleanField(default=False)
	message = models.ForeignKey(Message, on_delete=models.CASCADE, null=True)
	created_at = models.DateTimeField(null=True, auto_now_add=True)
	channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
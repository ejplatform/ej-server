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

	class Meta:
		ordering = ['title']
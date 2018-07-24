import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from ej_users.models import User

class Channel(models.Model):
	name = models.CharField(max_length=100)
	users = models.ManyToManyField(User, blank=True)
	created_at = models.DateTimeField(null=True, auto_now_add=True)
from django.db import models

from ej_users.models import User


class Channel(models.Model):
    name = models.CharField(max_length=100)
    users = models.ManyToManyField(User, blank=True)
    sort = models.CharField(max_length=100, default="admin")
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="channel_owner")

    class Meta:
        ordering = ['id']

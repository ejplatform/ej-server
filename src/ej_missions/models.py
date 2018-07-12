import logging

from django.db import models
from ej_users.models import User
from ej_trophies.models.trophy import Trophy
from ej_trophies.models.user_trophy import UserTrophy
from django.db.models.signals import post_save
from django.dispatch import receiver


def mission_directory_path(instance, filename):
    return 'uploads/mission_{0}/{1}'.format(instance.mission.id, filename)

class Mission(models.Model):

    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    reward = models.TextField(max_length=1000, null=True)
    #who is doing the mission
    users = models.ManyToManyField(User, blank=True)
    youtubeVideo = models.CharField(max_length=60, blank=True, null=True)
    image = models.FileField(upload_to="missions",
                                  default="default.jpg")
    audio = models.FileField(upload_to="missions",
                                  default="default.jpg")
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name="owner", null=True)
    trophy = models.ForeignKey(Trophy, on_delete=models.CASCADE, null=True)
    deadline = models.DateField(null=True)
    created_at = models.DateTimeField(null=True, auto_now_add=True)

    class Meta:
        ordering = ['title']

class Receipt(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    userName = models.CharField(max_length=30)
    userEmail = models.CharField(max_length=60)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=60)
    description = models.CharField(max_length=60)
    receiptFile  = models.FileField(upload_to="media/missions",
                                    default="media/default.jpg")

class Comment(models.Model):
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=280)

@receiver(post_save, sender=Receipt)
def update_trophy(sender, **kwargs):
    instance = kwargs.get('instance')
    if (instance.status == "realized"):
        mission_trophy = instance.mission.trophy
        user = instance.user
        user_trophy = UserTrophy.objects.get(trophy=mission_trophy,
                                             user=user)
        user_trophy.percentage = 100
        user_trophy.save(force_update=True)

import logging

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel, StatusModel
from django.conf import settings

from boogie import rules
from boogie.rest import rest_api
from ej_users.models import User


def mission_directory_path(instance, filename):
    return 'uploads/mission_{0}/{1}'.format(instance.mission.id, filename)

class Mission(models.Model):

    title = models.CharField(max_length=30)
    description = models.TextField(max_length=1000)
    #who is doing the mission
    users = models.ManyToManyField(User)
    youtubeVideo = models.CharField(max_length=60, default="")
    image = models.FileField(upload_to="missions",
                                  default="default.jpg")
    audio = models.FileField(upload_to="missions",
                                  default="default.jpg")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, 
                             related_name="owner", null=True)

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


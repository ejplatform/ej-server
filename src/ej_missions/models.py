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
    users = models.ManyToManyField(User)
    youtubeVideo = models.CharField(max_length=60)
    fileUpload = models.FileField(upload_to="uploads",
                                  default=settings.MEDIA_ROOT + "/uploads/default.jpg")

    class Meta:
        ordering = ['title']


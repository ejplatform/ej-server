import logging

from autoslug import AutoSlugField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from model_utils.models import TimeStampedModel, StatusModel

from boogie import rules
from boogie.rest import rest_api


@rest_api
class Mission(models.Model):

    title = models.CharField(max_length=30)
    description = models.TextField(max_length=1000)

from django.db.models.signals import post_save
from actstream import action
from ej.users.models import User
from django.utils.translation import ugettext as _
from django.dispatch import receiver



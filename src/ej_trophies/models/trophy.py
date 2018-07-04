import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _
from boogie.rest import rest_api

User = get_user_model()

def icon_path(field, instance, filename):
    filename = '{0}.{1}'.format(field, filename.split('.')[-1])
    return 'trophy_icons/{0}/{1}'.format(instance.key, filename)

def icon_not_started_path(instance, filename):
    return icon_path('not_started', instance, filename)

def icon_in_progress_path(instance, filename):
    return icon_path('in_progress', instance, filename)

def icon_complete_path(instance, filename):
    return icon_path('complete', instance, filename)

@rest_api(exclude=['users'], base_name='trophies', base_url='trophies')
class Trophy(models.Model):
    """
    Achievements available to users to complete and score points
    """
    users = models.ManyToManyField(
        User,
        through='UserTrophy',
        blank=True,
        verbose_name=_('users')
    )

    required_trophies = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        verbose_name=_('required trophies')
    )

    key = models.CharField(
        _('reference key'),
        unique=True,
        max_length=20,
        help_text=_('Trophy unique key defined by human in order to manage static references')
    )

    name = models.CharField(
        _('name'),
        unique=True,
        max_length=40
    )

    short_description = models.CharField(
        _('short description'),
        blank=True,
        max_length=50
    )

    full_description = models.TextField(
        _('full description'),
        blank=True
    )

    completion_message = models.TextField(
        _('completion message'),
        blank=True,
        max_length=100,
        default=_('Congratulations for your achievement! You are awesome!'),
        help_text=_('Trophy completion message is used to congratulate the user after the achievement of the trophy')
    )

    icon_not_started = models.ImageField(
        upload_to=icon_not_started_path,
        verbose_name=_('icon when it is not started')
    )

    icon_in_progress = models.ImageField(
        upload_to=icon_in_progress_path,
        verbose_name=_('icon when it is progress')
    )

    icon_complete = models.ImageField(
        upload_to=icon_complete_path,
        verbose_name=_('icon when it is complete')
    )

    score_percent = models.PositiveIntegerField(
        _('score for each percent of completion'),
        blank=True,
        default=0
    )

    score_completed = models.PositiveIntegerField(
        _('score for completion'),
        blank=True,
        default=0
    )

    complete_on_required_satisfied = models.BooleanField(
        _('complete on requirements satisfied?'),
        blank=True,
        default=False,
        help_text=_('If set as True and the trophy has required trophies associated with, the completeness will be established automatically after all requirementes satisfied')
    )

    def __str__(self):
        return self.key

    class Meta:
        verbose_name_plural = _('trophies')

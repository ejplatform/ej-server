from random import choice

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from faker import Factory

from boogie import rules
from boogie.apps.users.models import AbstractUser
from boogie.rest import rest_api
from .manager import UserManager
from ej_conversations.models import Conversation

fake = Factory.create('pt-BR')


@rest_api(['id', 'username', 'display_name'])
class User(AbstractUser):
    """
    Default user model for EJ platform.
    """

    display_name = models.CharField(
        _('Display name'),
        max_length=140,
        unique=True,
        help_text=_(
            'A randomly generated name used to identify each user.'
        ),
    )
    objects = UserManager()
    favorite_conversations = models.ManyToManyField(Conversation)

    @property
    def profile(self):
        profile = rules.get_value('auth.profile')
        return profile(self)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = random_name()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if not rules.test_rule('auth.valid_username', self.username):
            error = {'username': _('invalid username: %s') % self.username}
            raise ValidationError(error)

    def update_favorite_conversation_status(self, conversation):
        if self.favorite_conversations.filter(id=conversation.id).exists():
            self.favorite_conversations.remove(conversation)
        else:
            self.favorite_conversations.add(conversation)

    class Meta:
        swappable = 'AUTH_USER_MODEL'


def random_name(fmt='{adjective} {noun}'):
    x = ['foo', 'bar', 'baz']
    for _iter in range(100):
        name = fake.name()
        name = fmt.format(adjective=choice(x), noun=name)
        if not User.objects.filter(display_name=name):
            return name
    else:
        raise RuntimeError(
            'maximum number of attempts reached when trying to generate a '
            'unique random name'
        )

from random import choice

from django.db import models
from django.utils.translation import ugettext_lazy as _
from faker import Factory

from boogie import rules
from boogie.apps.users.models import AbstractUser
from boogie.rest import rest_api
from .manager import UserManager

fake = Factory.create('pt-BR')


@rest_api(['id', 'display_name', 'favorite_conversations'])
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
    email = models.EmailField(
        _('email address'),
        blank=True,
        unique=True,
    )
    objects = UserManager()
    favorite_conversations = models.ManyToManyField(
        'ej_conversations.Conversation'
    )

    @property
    def username(self):
        return self.email.replace('@', '__')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    @property
    def profile(self):
        profile = rules.get_value('auth.profile')
        return profile(self)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = random_name()
        super().save(*args, **kwargs)

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

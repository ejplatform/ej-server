from random import choice

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from faker import Factory

from boogie import rules
from boogie.apps.users.models import AbstractUser
from boogie.rest import rest_api
from .manager import UserManager

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

    @property
    def profile(self):
        profile = rules.get_value('auth.profile')
        return profile(self)

    def save(self, *args, **kwargs):
        if not self.display_name:
            self.display_name = random_name()
        super().save(*args, **kwargs)

    # def clean(self):
    #     super().clean()
    #     if not rules.test_rule('auth.valid_username', self.username):
    #         error = {'username': _('invalid username: %s') % self.username}
    #         raise ValidationError(error)

    class Meta:
        swappable = 'AUTH_USER_MODEL'


def username(full_name, email):
    names = list(filter(None, full_name.split(' ')))
    first_name = names[0].lower()
    normalized_email = email.split('@')[0].replace('.', '_')

    if not User.objects.filter(username=first_name):
        return first_name
    elif not User.objects.filter(username=normalized_email):
        return normalized_email
    else:
        try:
            return username_by_name_combination(names)
        except RuntimeError:
            return username_by_email(normalized_email)


def username_by_name_combination(names):
    for _iter in range(len(names)):
        if _iter < len(names) - 1:
            username = (names[_iter] + names[_iter + 1]).lower()
            if not User.objects.filter(username=username):
                return username
    else:
        raise RuntimeError(
            'no valid unique names combination found'
        )


def username_by_email(email):
    for _iter in range(100):
        username = email + str(_iter)
        if not User.objects.filter(username=username):
            return username
    else:
        raise RuntimeError(
            'maximum number of attempts reached when trying to generate a '
            'unique username by user email'
        )


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

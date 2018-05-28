from django.contrib.auth.models import UserManager as BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from boogie import rules


class UserManager(BaseUserManager):
    def get_by_email_or_username(self, value):
        """
        Return a user with the given e-mail or username.
        """
        if '@' in value:
            return self.get(email=value)
        else:
            return self.get(username=value)

    def normalize_username(self, username):
        if not username:
            msg = _('username is empty')
            raise ValidationError({'username': msg})
        if '@' in username:
            msg = _('username cannot have the "@: character')
            raise ValidationError({'username': msg})
        rule = rules.get_rule('ej_users.valid_username')
        if not rule.test(username):
            msg = _('invalid username: {username}').format(username=username)
            raise ValidationError({'username': msg})
        return username

    def _create_user(self, username, email, password, name='', **extra):
        username = self.normalize_username(username)
        extra['name'] = name or _('anonymous user')
        return super()._create_user(username, email, password, **extra)

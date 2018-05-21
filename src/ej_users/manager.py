import random
import string

from django.contrib.auth.models import UserManager as BaseUserManager
from django.db import IntegrityError


class UserManager(BaseUserManager):
    def get_by_email_or_username(self, value):
        """
        Return a user with the given e-mail or username.
        """
        if '@' in value:
            return self.get(email=value)
        else:
            return self.get(username=value)

    def create_simple_user(self, name, email, password):
        """
        Create standard user from name, email and password.
        """
        if self.filter(email=email):
            raise IntegrityError(f'user with email {email} already exists')

        first_name, _, last_name = name.partition(' ')
        username = self.available_username(name, email)
        user = self.create(
            name=name,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            username=username,
        )
        user.set_password(password)
        user.save()
        return user

    def available_username(self, name, email):
        """
        Return an available username from name and e-mail information.
        """
        username, _, domain = email.partition('@')
        domain = domain.replace('-', '_')
        domain = domain.replace('.com', '')
        first_name = name.lower().partition(' ')[0]
        last_name = name.lower().partition(' ')[-1]
        last_name = last_name.replace(' ', '_')

        tests = [
            username,
            first_name,
            last_name,
            last_name + '_' + domain,
            username + '_' + domain,
        ]

        existing = set(
            self.filter(username__in=tests)
                .values_list('username', flat=True)
        )
        available = [name for name in tests if name not in existing]
        if available:
            return available[0]

        names = set(
            self
            .filter(username__startswith=username)
            .values_list('username', flat=True)
        )
        for i in range(1000):
            test = '%s_%s' % (username, i)
            if test not in names:
                return test
        return random_username()


def random_username():
    "A random username value with very low collision probability"

    return ''.join(random.choice(string.ascii_letters) for _ in range(20))

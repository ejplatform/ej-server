import random
import string
from logging import getLogger

from sidekick import lazy
from .exceptions import ApiError

log = getLogger('ej')


class RCConfigWrapper:
    @property
    def config(self):
        return self.configs.default_config()

    @property
    def url(self):
        return self.config.url

    @lazy
    def accounts(self):
        from .models import RCAccount
        return RCAccount.objects

    @lazy
    def configs(self):
        from .models import RCConfig
        return RCConfig.objects

    @property
    def has_config(self):
        return self.configs.default_config(raises=False) is not None

    def register(self, user, username):
        """
        Call Rocket.Chat API to register a new user, if not already registered.
        """
        password = random_password(30)
        result = self.api_call(
            'users.create',
            auth='admin',
            raises=False,
            payload={
                'email': user.email,
                'name': user.name,
                'username': username,
                'password': password,
            },
        )

        if not result['success']:
            error = result['error']
            log.warning(f'Could not create Rocket.Chat user: {error}')
            raise ApiError(result)

        # Account created successfully in Rocket.Chat, create a replica in
        # Django
        return self.accounts.create(
            config=self.config,
            user=user,
            username=username,
            password=password,
            user_rc_id=result['user']['_id'],
            is_active=True,
        )

    def login(self, user):
        """
        Force Django user to login at Rocket.Chat.

        User must already been registered and provided a RC username.
        """
        account = self.accounts.get(user=user)
        if not account.is_active:
            return account

        payload = {'username': account.username, 'password': account.password}
        response = self.api_call('login', payload=payload, auth=None)
        log.info(f'{user} successfully logged in at Rocket.Chat')
        account.auth_token = response['data']['authToken']
        account.save()
        return account

    def logout(self, user):
        """
        Force logout of Django user.
        """
        users = list(self.accounts.filter(user=user))
        if not users:
            return

        account = users[0]
        user_id, auth_token = account.user_rc_id, account.auth_token
        if auth_token:
            auth = {'user_id': user_id, 'auth_token': auth_token}
            self.api_call('logout', auth=auth, method='post')
            account.auth_token = ''
            account.save()
            log.info(f'{user} successfully logged out from Rocket.Chat')

    def login_token(self, user):
        """
        Return the login auth token for the given user.
        """
        return self.accounts.get(user=user).auth_token

    def api_call(self, *args, **kwargs):
        """
        Calls Rocket.Chat API and return the response.

        Raise ApiError if response code is not 200.
        """
        return self.config.api_call(*args, **kwargs)

    def api_user_update(self, id, **kwargs):
        """
        Update user with parameters.

        Example:
            >>> rocket.api_user_update(user_id, password='pass1234word')
        """
        payload = {'userId': id, 'data': kwargs}
        result = self.api_call(f'users.update', payload=payload, auth='admin')
        return result['user']

    def find_or_create_account(self, user):
        """
        Tries to find and create a rocket user account for the given user.

        This method does not check if user has permission and can create a
        RC account even for a user that does not have the proper permission.

        Return None if no account is found.
        """
        try:
            return self.accounts.get(user=user)
        except self.accounts.model.DoesNotExist:
            pass
        return None


rocket = RCConfigWrapper()


def random_password(size):
    return ''.join(random.choice(string.ascii_letters) for _ in range(size))

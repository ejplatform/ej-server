import json

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .exceptions import ApiError
from .manager import RCConfigManager

CAN_LOGIN_PERM = 'ej_rocketchat.can_create_account'


class RCAccount(models.Model):
    """
    Register subscription of a EJ user into rocket
    """

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='rocketchat_subscription',
    )
    username = models.CharField(
        _('Username'),
        max_length=50,
        help_text=_(
            'Username that identifies you in the Rocket.Chat platform.\n'
            'Use small names with letters and dashes such as @my-user-name.'
        ),
    )
    password = models.CharField(
        _('Password'),
        max_length=50,
    )

    user_rc_id = models.CharField(
        _('Rocketchat user id'),
        max_length=50,
    )
    auth_token = models.CharField(
        _('Rocketchat user token'),
        max_length=50,
        blank=True,
    )
    is_active = models.BooleanField(
        _('Is user active?'),
        default=True,
        help_text=_(
            'True for active Rocket.Chat accounts.'
        ),
    )
    rc_username = property(lambda self: f'ej-user-{self.user.id}')
    can_login_perm = CAN_LOGIN_PERM

    class Meta:
        verbose_name = _('Rocket.Chat Account')
        verbose_name_plural = _('Rocket.Chat Accounts')
        permissions = [
            (CAN_LOGIN_PERM.partition('.')[-1], _('Can login in the Rocket.Chat instance.')),
        ]

    def __str__(self):
        return f'{self.user} ({self.user_rc_id})'

    def update_info(self, commit=True):
        """
        Update user info from Rocketchat and user permissions.
        """
        config = RCConfig.objects.default_config()
        self.user_rc_id, self.auth_token = config.user_info(self.user)
        if commit:
            self.save()


class RCConfig(models.Model):
    """
    Store Rocketchat configuration.
    """
    url = models.URLField(
        _('Rocket.Chat URL'),
        unique=True,
        default=settings.EJ_ROCKETCHAT_URL,
        help_text=_(
            'Public URL in which the Rocket.Chat instance is installed.'
        ),
    )
    api_url = models.URLField(
        _('Rocket.Chat private URL'),
        unique=True,
        help_text=_(
            'A private URL used only for API calls. Can be used to override '
            'the public URL if Rocket.Chat is available in an internal '
            'address in your network.'
        )
    )
    admin_id = models.CharField(
        _('Admin user id'),
        max_length=50,
        help_text=_(
            'Id string for the Rocket.Chat admin user.',
        ),
    )
    admin_token = models.CharField(
        _('Login token'),
        max_length=50,
        help_text=_(
            'Login token for the Rocket.Chat admin user.',
        )
    )
    is_active = models.BooleanField(
        _('Is active'),
        default=True,
        help_text=_(
            'Set to false to temporarily disable RocketChat integration.'
        ),
    )

    objects = RCConfigManager()

    class Meta:
        verbose_name = _('Rocket.Chat Configuration')
        verbose_name_plural = _('Rocket.Chat Configurations')

    def __str__(self):
        return f'Rocket config: {self.url} ({self.admin_id})'

    def api_call(self, uri, version='v1', payload=None, args=None, headers=None, raises=True, method='post', auth=None):
        """
        Makes a call to Rocketchat API.

        Args:
            uri, version:
                Used to contruct rocketchat url as <rocketchat>/api/<version>/<uri>
            user:
                User making the request.
            admin (bool):
                If set to True, makes the request as the admin user.
            payload (JSON):
                If given, makes a POST request with the given payload.

        Examples:
            >>> rocketchat_url('users.create', admin=True)
            http://rocketchat:3000/api/v2/users.create

        """
        # Construct base url
        url_base = self.api_url or self.url
        if '://' not in url_base:
            url_base = 'http://' + url_base
        url = f'{url_base}/api/{version}/{uri}'

        # Extra parameters
        kwargs = {}

        # Headers
        headers = dict(headers or {})
        if auth:
            if auth == 'admin':
                id, token = self.admin_id, self.admin_token
            elif isinstance(auth, dict):
                id, token = auth['user_id'], auth['auth_token']
            else:
                id, token = self.user_info(auth)
            headers.update({'X-Auth-Token': token, 'X-User-Id': id})

        # Payload
        if payload is not None and method == 'post':
            kwargs['data'] = json.dumps(payload)
            headers['Content-Type'] = 'application/json'
        method = getattr(requests, method)

        # Query args
        if args:
            query_param = '&'.join(f'{k}={v}' for k, v in args.items())
            url = f'{url}?{query_param}'

        # Makes API request
        response = method(url, headers=headers, **kwargs)
        result = json.loads(response.content, encoding='utf-8')
        if response.status_code != 200 and raises:
            error = {'code': response.status_code, 'response': result}
            raise ApiError(error)
        return result

    def user_info(self, user):
        """
        Fetches Rocketchat user information.

        Args:
            user: Django user.

        See also:
            https://rocket.chat/docs/developer-guides/rest-api/miscellaneous/info/
        """
        account = RCAccount.objects.get(user=user)
        payload = {'username': self.username}
        result = self.api_call('users.info', auth='admin', payload=payload)

        if result.get('status') == 'error':
            raise PermissionError(result)
        elif result.get('errorType') == 'error-invalid-user':
            raise ValueError('invalid username')
        return result


def api_call(*args, **kwargs):
    return RCConfig.objects.default_config().api_call(*args, **kwargs)

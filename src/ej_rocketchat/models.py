import json
from json import JSONDecodeError

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from ej.utils import JSONField
from .exceptions import ApiError
from .manager import RCConfigManager

CAN_LOGIN_PERM = 'ej_rocketchat.can_create_account'


class RCAccount(models.Model):
    """
    Register subscription of a EJ user into rocket
    """

    config = models.ForeignKey(
        'RCConfig',
        on_delete=models.CASCADE,
    )
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
        validators=[
            RegexValidator(
                r'^\@?(\w+-)*\w+$',
                message=_(
                    'Username must consist of letters, numbers and dashes.'
                )
            )
        ],
    )
    password = models.CharField(
        _('Password'),
        max_length=50,
        blank=True,
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
    account_data = JSONField(
        _('Account data'),
        null=True, blank=True,
        help_text=_('JSON-encoded data for user account.')
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
        blank=True,
        null=True,
        help_text=_(
            'A private URL used only for API calls. Can be used to override '
            'the public URL if Rocket.Chat is available in an internal '
            'address in your network.'
        )
    )
    admin_username = models.CharField(
        _('Admin username'),
        max_length=50,
        default='ej-admin',
        help_text=_(
            'Username for Rocket.Chat admin user'
        ),
    )
    admin_password = models.CharField(
        _('Password'),
        max_length=50,
        help_text=_(
            'Password for the administrative account. It is unfortunately '
            'necessary to store this value since Rocket.Chat authentication '
            'tokens expire at unpredictable times.'
        ),
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
                Used to construct Rocket.Chat url as <rocketchat>/api/<version>/<uri>
            payload (JSON):
                JSON payload for the request
            args (dict):
                Query dictionary appended to the url.
            headers (dict):
                An optional dictionary of HTTP headers.
            raises (bool):
                If True (default) raises an ApiError for bad responses from the
                API, otherwise, return the response dictionary.
            method ('post', 'get'):
                HTTP method used on the request.
            auth:
                Either None, a user with a registered Rocket.Chat account or
                the string 'admin' for admin access to the API.
        """
        url = normalize_api_url(self.api_url or self.url, version, uri, args)
        headers = normalize_headers(headers, auth, self)
        kwargs = {}

        # Payload
        if payload is not None and method == 'post':
            kwargs['data'] = json.dumps(payload)
            headers['Content-Type'] = 'application/json'
        method = getattr(requests, method)

        # Makes API request
        try:
            response = method(url, headers=headers, **kwargs)
            result = json.loads(response.content, encoding='utf-8')
        except (requests.ConnectionError, JSONDecodeError) as exc:
            msg = {
                'status': 'error',
                'message': str(exc),
                'error': type(exc).__name__,
            }
            if raises:
                raise ApiError(msg)
            return msg
        if response.status_code != 200 and raises:
            error = {'code': response.status_code, 'response': result}
            raise ApiError(error)
        return result


def normalize_api_url(base, version, uri, args=None):
    if '://' not in base:
        base = 'http://' + base

    query = ''
    if args:
        query_param = '&'.join(f'{k}={v}' for k, v in args.items())
        query = f'?{query_param}'

    return f'{base}/api/{version}/{uri}{query}'


def normalize_headers(headers, auth, config):
    headers = dict(headers or {})
    if auth:
        if auth == 'admin':
            id, token = config.admin_id, config.admin_token
        elif isinstance(auth, dict):
            id, token = auth['user_id'], auth['auth_token']
        else:
            id, token = config.user_info(auth)
        headers.update({'X-Auth-Token': token, 'X-User-Id': id})
    return headers

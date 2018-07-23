import random
import string
import json
import requests

from django.core.cache import cache
from constance import config


def rc_token_cache_key(username):
    """
    Gives an unique cache key to an user
    """
    return f'rc_token_{username}'


def rocketchat_url(uri, api_version='v1'):
    """
    Build a Rocketchat API URL based on django constance configurations

    Args:
        uri (str):
            Final piece of the rocketchat API URL
        api_version (str):
            Version of the Rocketchat API

    Examples:
        >>> rocketchat_url('users.create', 'v2')
        http://rocketchat:3000/api/v2/users.create

    """
    return (f'{config.ROCKETCHAT_PRIVATE_URL or config.ROCKETCHAT_URL}'
            f'/api/{api_version}/{uri}')


def create_rc_user_token(email, name, username):
    """
    Creates a new rocketchat user if it's username is not registered on the
    service and returns a valid login token.

    Args:
        email (str):
            Django user email.
        name (str):
            Django user fullname.
        username (str):
            Django user username.
    """
    if not is_rc_user_registered(username):
        create_rc_user(email, name, username)

    return get_rc_user_token(username)


def create_rc_user(email, name, username):
    """
    Calls Rocketchat API to create a new user with the same information of
    the django user.

    Args:
        email (str):
            Django user email.
        name (str):
            Django user fullname.
        username (str):
            Django user username.

    See also:
        https://rocket.chat/docs/developer-guides/rest-api/users/create/
    """
    json_data = {
        'email': email,
        'name': name,
        'username': username,
        'password': _make_pass(30),
    }
    res = requests.post(
        rocketchat_url('users.create'),
        headers=get_headers(),
        json=json_data,
    )
    if res.status_code != 200:
        raise Exception(f'Error: {res.content}')


def get_rc_user_token(username):
    """
    Get a cached user's rocketchat login token or require a new one and
    update the cache.

    Args:
        username (str):
            Django user username.

    Example:
        >>> get_rc_user_token('example')
        'rc_token_example'
    """
    return cache.get_or_set(
        rc_token_cache_key(username),
        generate_rc_user_token(username),
    )


def generate_rc_user_token(username):
    """
    Request a new user's login token to the Rocketchat API

    Args:
        username (str):
            Django user username.

    See also:
        https://rocket.chat/docs/developer-guides/rest-api/users/createtoken/
    """
    json_data = {
        'username': username,
    }
    res = requests.post(
        rocketchat_url('users.createToken'),
        headers=get_headers(),
        data=json_data,
    )
    if res.status_code != 200:
        raise Exception(f'Error: {res.content}')
    return json.loads(res.content)['data']['authToken']


def invalidade_rc_user_token(username):
    """
    Invalidates the user cached token using Rocketchat API

    Args:
        username (str):
            Django user username.

    See also:
        https://rocket.chat/docs/developer-guides/rest-api/authentication/logout/
    """
    try:
        user_info = json.loads(request_rc_user_info(username).content)['user']
        token = cache.get(rc_token_cache_key(username))
        if token:
            res = requests.post(
                rocketchat_url('logout'),
                headers=get_headers(user_info['_id'], token),
            )
            cache.delete(rc_token_cache_key(username))
            if res.status_code != 200:
                raise Exception(f'Error: {res.content}')
    except KeyError:
        return False

    return True


def request_rc_user_info(username):
    """
    Request Rocketchat user information.

    Args:
        username (str):
            Django user username.

    See also:
        https://rocket.chat/docs/developer-guides/rest-api/miscellaneous/info/
    """
    return requests.get(
        rocketchat_url('users.info'),
        headers=get_headers(),
        params=dict(username=username)
    )


def is_rc_user_registered(username):
    """
    Check username is registered on Rocketchat service

    Args:
        username (str):
            Django user username.
    """
    res = request_rc_user_info(username)
    return res.status_code == 200


def get_headers(user_id=None, auth_token=None):
    """
    Builds the request header for the rocketchat api calling

    Args:
        user_id (str):
            Rocketchat user id.
        auth_token (str):
            Rocketchat user's auth token.
    """
    return {
        'X-Auth-Token': auth_token or config.ROCKETCHAT_AUTH_TOKEN,
        'X-User-Id': user_id or config.ROCKETCHAT_USER_ID,
    }


def _make_pass(n):
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(n))

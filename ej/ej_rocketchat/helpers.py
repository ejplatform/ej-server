import random
import string
import requests
import json
import sys

from django.core.cache import cache
from constance import config


def rc_token_cache_key(username):
    return f'rc_token_{username}'


def rocketchat_url(uri):
    return (config.ROCKETCHAT_PRIVATE_URL or config.ROCKETCHAT_URL) + uri


def create_rc_user_token(email, name, username):
    if not is_rc_user_registered(username):
        create_rc_user(email, name, username)

    return get_rc_user_token(username)


def create_rc_user(email, name, username):
    json_data = {
        'email': email,
        'name': name,
        'username': username,
        'password': make_pass(30),
    }
    res = requests.post(
        rocketchat_url('/api/v1/users.create'),
        headers=get_headers(),
        json=json_data,
    )
    if res.status_code != 200:
        raise Exception(f'Error: {res.content}')


def get_rc_user_token(username):
    return cache.get_or_set(
        rc_token_cache_key(username),
        generate_rc_user_token(username),
    )


def generate_rc_user_token(username):
    json_data = {
        'username': username,
    }
    res = requests.post(
        rocketchat_url('/api/v1/users.createToken'),
        headers=get_headers(),
        data=json_data,
    )
    if res.status_code != 200:
        raise Exception(f'Error: {res.content}')
    return json.loads(res.content)['data']['authToken']


def invalidade_rc_user_token(username):
    user_info = json.loads(request_rc_user_info(username).content)['user']
    token = cache.get(rc_token_cache_key(username))
    if token:
        res = requests.post(
            rocketchat_url('/api/v1/logout'),
            headers=get_headers(user_info['_id'], token),
        )
        cache.delete(rc_token_cache_key(username))
        if res.status_code != 200:
            raise Exception(f'Error: {res.content}')
    

def request_rc_user_info(username):
    return requests.get(
        rocketchat_url('/api/v1/users.info'),
        headers=get_headers(),
        params=dict(username=username)
    )


def is_rc_user_registered(username):
    res = request_rc_user_info(username) 
    return res.status_code == 200


def get_headers(user_id=None, auth_token=None):
    return {
        'X-Auth-Token': auth_token or config.ROCKETCHAT_AUTH_TOKEN,
        'X-User-Id': user_id or config.ROCKETCHAT_USER_ID,
    }


def make_pass(n):
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(n))

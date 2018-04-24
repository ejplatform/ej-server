import random
import string
import requests
import sys
import json

from constance import config


rocketchat_url = lambda uri: config.ROCKETCHAT_URL + uri


def create_user_token(email, name, username):
    if not is_user_registered(username):
        create_rc_user(email, name, username)

    return get_user_token(username)


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


def get_user_token(username):
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


def is_user_registered(username):
    json_data = {
        'username': username,
    }
    res = requests.post(
        rocketchat_url('/api/v1/users.info'),
        headers=get_headers(),
        params=json_data
    )
    return res.status_code == 200


def get_headers():
    return {
        'X-Auth-Token': config.ROCKETCHAT_AUTH_TOKEN,
        'X-User-Id': config.ROCKETCHAT_USER_ID,
    }


def make_pass(n):
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(n))

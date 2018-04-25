import random
import string
import requests
import json

from constance import config


def rocketchat_url(uri):
    return (config.ROCKETCHAT_PRIVATE_URL or config.ROCKETCHAT_URL) + uri


def create_rc_user_token(email, name, username):
    if not is_rc_user_registered(username):
        create_rc_user(email, name, username)

    enable_rc_user_login(username, True)
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


def enable_rc_user_login(username, option):
    info = json.loads(request_rc_user_info(username).content)
    rc_user_id = info['user']['_id']
    json_data = {
        'userId': rc_user_id,
        'data': {
            'active': option
        }
    }
    res = requests.post(
        rocketchat_url('/api/v1/users.update'),
        headers=get_headers(),
        json=json_data,
    )
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


def get_headers():
    return {
        'X-Auth-Token': config.ROCKETCHAT_AUTH_TOKEN,
        'X-User-Id': config.ROCKETCHAT_USER_ID,
    }


def make_pass(n):
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(n))

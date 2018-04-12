import random
import string
import requests
import sys
import json

from pymongo import MongoClient
from django.conf import settings


def create_user_token(email, name, username):
    client = MongoClient(settings.MONGO_URL)
    if settings.MONGO_URL.count('/') > 2:
        mongo = client.get_default_database()
    else:
        mongo = client.rocketchat

    if not mongo.users.find_one({'username': username}):
        create_rc_user(email, name, username)

    return get_user_token(username)


def create_rc_user(email, name, username):
    headers = {
        'X-Auth-Token': settings.ROCKETCHAT_AUTH_TOKEN,
        'X-User-Id': settings.ROCKETCHAT_USER_ID,
    }
    json_data = {
        'email': email,
        'name': name,
        'username': username,
        'password': make_pass(30),
    }
    res = requests.post(
        settings.ROCKETCHAT_URL + '/api/v1/users.create',
        headers=headers,
        json=json_data,
    )
    if res.status_code != 200:
        raise Exception(f'Error: {res.content}')
    

def get_user_token(username):
    headers = {
        'X-Auth-Token': settings.ROCKETCHAT_AUTH_TOKEN,
        'X-User-Id': settings.ROCKETCHAT_USER_ID,
    }
    json_data = {
        'username': username,
    }
    res = requests.post(
        settings.ROCKETCHAT_URL + '/api/v1/users.createToken',
        headers=headers,
        data=json_data,
    )
    if res.status_code != 200:
        raise Exception(f'Error: {res.content}')
    return json.loads(res.content)['data']['authToken']


def make_pass(n):
    return ''.join(random.SystemRandom().choice(
        string.ascii_uppercase + string.digits) for _ in range(n))

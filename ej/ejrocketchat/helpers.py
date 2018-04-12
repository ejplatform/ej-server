import hashlib
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
        'password': generate_token(),
    }
    resp = requests.post(
        settings.ROCKETCHAT_URL + '/api/v1/users.create',
        headers=headers,
        json=json_data,
    )
    if resp.status_code != 200:
        raise Exception(f'Error: {resp.content}')
    

def get_user_token(username):
    headers = {
        'X-Auth-Token': settings.ROCKETCHAT_AUTH_TOKEN,
        'X-User-Id': settings.ROCKETCHAT_USER_ID,
    }
    json_data = {
        'username': username,
    }
    resp = requests.post(
        settings.ROCKETCHAT_URL + '/api/v1/users.createToken',
        headers=headers,
        data=json_data,
    )
    return json.loads(resp.content)['data']['authToken']

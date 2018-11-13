import json
import pytest

from django.test.client import Client
from django.contrib.auth.models import AnonymousUser

from ej_conversations import create_conversation
from ej_users.models import User


@pytest.fixture
def user(db):
    user = User.objects.create_user('email@server.com', 'password')
    user.board_name = 'testboard'

    # TODO: Fix this dirty way to set user permissions
    user.has_perm = lambda x, y=None: True

    user.save()
    return user


@pytest.fixture
def conversation(db, user):
    return create_conversation(text='test', title='title', author=user, is_promoted=True)


@pytest.fixture
def comment(db, conversation, user):
    return conversation.create_comment(user, 'content', 'approved')


@pytest.fixture
def vote(db, user, comment):
    return comment.vote(author=user, choice='agree')


@pytest.fixture
def post_request(rf):
    request = rf.post('')
    request.user = AnonymousUser()
    return request


@pytest.fixture
def request_(rf):
    request = rf.get('')
    request.user = AnonymousUser()
    return request


@pytest.fixture
def request_with_user(rf, user):
    request = rf.get('/testboard/')
    request.user = user
    return request


@pytest.fixture
def mk_user(db, email='default@user.com', is_staff=False):
    return User.objects.create_user(email, '1234', is_staff=is_staff)


@pytest.fixture
def api(client):
    return ApiClient(client)


class ApiClient:
    def __init__(self, client: Client):
        self.client = client

    def _result(self, data, fields=None, exclude=(), skip=()):
        if fields is not None:
            data = {k: v for k, v in data.items() if k in fields}
        for field in exclude:
            del data[field]
        for field in skip:
            data.pop(field, None)
        return data

    def _prepare(self, data):
        if isinstance(data, bytes):
            return data
        return json.dumps(data).encode('utf8')

    def get(self, url, raw=False, **kwargs):
        response = self.client.get(url)
        data = response if raw else response.data
        return self._result(data, **kwargs)

    def post(self, url, data, **kwargs):
        data = self._prepare(data)
        response = self.client.post(url, data, content_type='application/json')
        obj = json.loads(response.content)
        print(obj)
        return self._result(obj, **kwargs)

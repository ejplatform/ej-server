import json
import pytest

from django.test.client import Client
from ej_conversations.mommy_recipes import *


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

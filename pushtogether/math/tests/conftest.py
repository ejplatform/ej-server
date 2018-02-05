import pytest

from pushtogether.conversations.tests.conftest import *

from .helpers import create_valid_job

@pytest.fixture
def cluster_job(conversation):
    return create_valid_job(conversation)

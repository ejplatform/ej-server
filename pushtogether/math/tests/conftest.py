import pytest

from pushtogether.conversations.tests.conftest import *

from . import helpers

@pytest.fixture
def cluster_job(conversation):
    return helpers.create_valid_job(conversation)

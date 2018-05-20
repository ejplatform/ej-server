import pytest

# from ej_conversations.tests.conftest import *


@pytest.fixture
def cluster_job(conversation):
    from . import _helpers
    return _helpers.create_valid_job(conversation)

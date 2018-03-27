import pytest

from django.contrib.auth import get_user_model

from ej.conversations.models import (
    Conversation,
    Comment,
    Vote,
)

from .helpers import (
    create_valid_user,
    create_valid_conversation,
    create_valid_comment,
    create_valid_vote
)

@pytest.fixture
def user():
    return create_valid_user("test_user")

@pytest.fixture
def other_user():
    return create_valid_user("other_test_user")

@pytest.fixture
def conversation(user):
    return create_valid_conversation(user)

@pytest.fixture
def comment(conversation, user):
    return create_valid_comment(conversation, user)

@pytest.fixture
def vote(comment, user):
    return create_valid_vote(comment, user)

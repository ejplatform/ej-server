import pytest

from django.contrib.auth import get_user_model

from pushtogether.conversations.models import (
    Conversation,
    Comment,
    Vote,
)


pytestmark = pytest.mark.django_db


class TestConversation:
    def test_save(self):
        user = get_user_model().objects.create(
            username="test_user",
        )

        conversation = Conversation.objects.create(
            author=user,
            title="test_title",
            description="test_description",
        )
        conversation.save()
        assert conversation.title == "test_title"
        assert conversation.description == "test_description"

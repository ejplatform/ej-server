import pytest

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

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


class TestComment:
    def setup(self):
        self.user = get_user_model().objects.create(
            username="test_user",
            password="test_password",
            first_name="test",
            last_name="user",
            is_superuser=True,
        )
        self.user.save()

        self.conversation = Conversation.objects.create(
            author=self.user,
            title="test_title",
            description="test_description",
        )
        self.conversation.save()

    def test_nudge_acceptance(self):
        self.conversation.comment_nudge = 4
        self.conversation.comment_nudge_interval = 10
        old_user_comment_counter = self.user.comments.count()

        for i in range(4):
            try:
                Comment.objects.create(
                    author=self.user,
                    conversation=self.conversation,
                    content="test_content",
                    approval=Comment.APPROVED
                )
            except ValidationError:
                pass

        new_user_comment_counter = self.user.comments.count()
        assert new_user_comment_counter - old_user_comment_counter == 4
        

    def test_nudge_rejection(self):
        self.conversation.comment_nudge = 2
        self.conversation.comment_nudge_interval = 10
        old_user_comment_counter = self.user.comments.count()

        for i in range(4):
            try:
                Comment.objects.create(
                    author=self.user,
                    conversation=self.conversation,
                    content="test_content",
                    approval=Comment.APPROVED
                )
            except ValidationError:
                pass

        new_user_comment_counter = self.user.comments.count()
        assert new_user_comment_counter - old_user_comment_counter == 2

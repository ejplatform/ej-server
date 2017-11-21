import pytest

from django.contrib.auth import get_user_model

from pushtogether.conversations.models import (
    Conversation,
    Comment,
    Vote,
)


pytestmark = pytest.mark.django_db


class TestBase:

    def setup(self):
        self.user = self.create_valid_user("test_user")
        self.other_user = self.create_valid_user("other_user")
        self.conversation = self.create_valid_conversation(self.user)

    def create_valid_user(self, username):
        user = get_user_model().objects.create(
            username=username,
            password="test_password",
            first_name="test",
            last_name="user",
            is_superuser=True,
        )
        user.set_password("test_password")
        user.save()
        return user

    def create_valid_conversation(self, user):
        conversation = Conversation.objects.create(
            author=user,
            title="test_title",
            description="test_description",
        )
        conversation.save()
        return conversation

    def create_valid_comment(self, conversation, user, approval=Comment.APPROVED):
        comment = Comment.objects.create(
            author=user,
            conversation=conversation,
            content="test_content",
            polis_id='1234',
            approval=approval
        )
        comment.save()
        return comment

    def create_valid_comments(self, number, conversation, user, approval=Comment.APPROVED):
        return [self.create_valid_comment(conversation, user, approval)
                for x in range(number)]

    def create_valid_vote(self, comment, user, value=Vote.AGREE):
        vote = Vote.objects.create(
            author=user,
            comment=comment,
            polis_id='12345',
            value=Vote.AGREE
        )
        vote.save()
        return vote

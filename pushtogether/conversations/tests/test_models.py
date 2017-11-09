import pytest
import datetime
from pprint import pprint

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware, get_current_timezone

from pushtogether.conversations.models import (
    Conversation,
    Comment,
    Vote,
)


pytestmark = pytest.mark.django_db


class TestConversation:
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

    def teardown(self):
        self.conversation.comments.all().delete()
        assert self.conversation.comments.count() == 0

    def create_valid_comment(self, conversation, user):
        comment = Comment.objects.create(
            author=user,
            conversation=conversation,
            content="test_content",
            polis_id='1234',
            approval=Comment.APPROVED
        )
        comment.save()

    def test_create_valid_comment(self):
        old_counter = self.conversation.comments.count()
        self.create_valid_comment(self.conversation, self.user)
        new_counter = self.conversation.comments.count()

        assert old_counter == 0
        assert new_counter == 1

    def test_nudge_enum_status_codes(self):
        '''
        Nudge blocked status should return too many request http status code (429)
        Eager and normal status should return a success http status code (200)
        '''
        assert self.conversation.NUDGE.interval_blocked.value['status_code'] == 429
        assert self.conversation.NUDGE.global_blocked.value['status_code'] == 429
        assert self.conversation.NUDGE.eager.value['status_code'] == 200
        assert self.conversation.NUDGE.normal.value['status_code'] == 200

    def test_nudge_get_datetime_interval(self):
        '''
        Time interval should be a datetime.now() past the interval arg
        '''
        for interval in [0, 1, 200]:
            now = datetime.datetime.now()
            past = self.conversation._get_datetime_interval(interval, now)
            timediff = make_aware(now, get_current_timezone()) - past
            assert timediff.seconds == interval

    def test_nudge_interval_comments(self):
        '''
        It should return only comments in specific interval
        '''
        self.conversation.comment_nudge_interval = 10  # seconds
        self.create_valid_comment(self.conversation, self.user)
        self.create_valid_comment(self.conversation, self.user)
        recent_user_comments = self.conversation._get_nudge_interval_comments(self.user)
        
        assert recent_user_comments.count() == self.conversation.comments.count()


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

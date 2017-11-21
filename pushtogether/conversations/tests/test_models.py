import pytest
import datetime
import time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware, get_current_timezone
from django.db.utils import IntegrityError

from pushtogether.conversations.models import (
    Conversation,
    Comment,
    Vote,
)

from .helpers import TestBase


pytestmark = pytest.mark.django_db


class TestConversation(TestBase):
    def setup(self):
        self.user = self.create_valid_user("test_user")
        self.other_user = self.create_valid_user("other_user")
        self.conversation = self.create_valid_conversation(self.user)

    def teardown(self):
        self.conversation.comments.all().delete()

    def test_create_valid_comment(self):
        old_counter = self.conversation.comments.count()
        self.create_valid_comment(self.conversation, self.user)
        new_counter = self.conversation.comments.count()

        assert old_counter == 0
        assert new_counter == 1

    def test_nudge_enum_status_codes(self):
        """
        Nudge blocked status should return too many request http status code (429)
        Eager and normal status should return a success http status code (200)
        """
        assert self.conversation.NUDGE.interval_blocked.value['status_code'] == 429
        assert self.conversation.NUDGE.global_blocked.value['status_code'] == 429
        assert self.conversation.NUDGE.eager.value['status_code'] == 200
        assert self.conversation.NUDGE.normal.value['status_code'] == 200

    def test_nudge_get_datetime_interval(self):
        """
        Time interval should be a datetime.now() past the interval arg
        """
        for interval in [0, 1, 200]:
            now = datetime.datetime.now()
            past = self.conversation._get_datetime_interval(interval, now)
            timediff = make_aware(now, get_current_timezone()) - past
            assert timediff.seconds == interval

    def test_nudge_interval_comments(self):
        """
        It should return only comments in specific interval
        """
        self.conversation.comment_nudge_interval = 1  # seconds
        self.create_valid_comment(self.conversation, self.user)
        time.sleep(2)
        self.create_valid_comments(2, self.conversation, self.user)
        recent_user_comments = self.conversation._get_nudge_interval_comments(self.user)

        assert recent_user_comments.count() == 2

    def test_nudge_is_user_eager_with_a_comment(self):
        """
        Should return true if user is trying to post too much comments
        """
        self.conversation.comment_nudge = 2
        self.conversation.comment_nudge_interval = 2
        self.create_valid_comment(self.conversation, self.user)
        user_comments = self.conversation._get_nudge_interval_comments(
            self.user)

        assert self.conversation._is_user_nudge_eager(
            user_comments.count(), user_comments) == True

    def test_nudge_is_user_eager_with_multiple_comments(self):
        """
        Should return true if user is trying to post too much comments
        """
        self.conversation.comment_nudge = 6
        self.conversation.comment_nudge_interval = 2
        self.create_valid_comments(3, self.conversation, self.user)
        user_comments = self.conversation._get_nudge_interval_comments(
            self.user)

        assert self.conversation._is_user_nudge_eager(
            user_comments.count(), user_comments) == True

    def test_nudge_is_user_eager_respecting_time_limit(self):
        """
        Should return false if user respect the time limit
        """
        self.conversation.comment_nudge = 4
        self.conversation.comment_nudge_interval = 2
        self.create_valid_comment(self.conversation, self.user)
        user_comments = self.conversation._get_nudge_interval_comments(
            self.user)

        assert self.conversation._is_user_nudge_eager(
            user_comments.count(), user_comments) == False

    def test_nudge_is_user_eager_distributing_comments_in_the_time(self):
        """
        Should return false if user respect the total time limit
        """
        self.conversation.comment_nudge = 4
        self.conversation.comment_nudge_interval = 1
        self.create_valid_comment(self.conversation, self.user)
        time.sleep(2)
        self.create_valid_comment(self.conversation, self.user)
        user_comments = self.conversation._get_nudge_interval_comments(
            self.user)

        assert self.conversation._is_user_nudge_eager(
            user_comments.count(), user_comments) == False

    def test_nudge_is_user_interval_blocked(self):
        """
        Should return true if user post too many comments disrescpecting time
        limits
        """
        self.conversation.comment_nudge = 1
        self.conversation.comment_nudge_interval = 10
        self.create_valid_comment(self.conversation, self.user)
        user_comments_counter = self.conversation._get_nudge_interval_comments(
            self.user).count()
        is_user_blocked = self.conversation._is_user_nudge_interval_blocked(
            user_comments_counter)

        assert is_user_blocked == True

    def test_nudge_is_user_interval_blocked_respecting_limits(self):
        """
        Should return false if user post comments moderately
        """
        self.conversation.comment_nudge = 2
        self.conversation.comment_nudge_interval = 10
        self.create_valid_comment(self.conversation, self.user)
        user_comments_counter = self.conversation._get_nudge_interval_comments(
            self.user).count()
        is_user_blocked = self.conversation._is_user_nudge_interval_blocked(
            user_comments_counter)

        assert is_user_blocked == False

    def test_nudge_is_user_global_limit_blocked(self):
        """
        Should return true if user post many comments disrespecting the
        nudge global limits
        """
        self.conversation.comment_nudge_global_limit = 1
        self.create_valid_comment(self.conversation, self.user)
        is_user_blocked = self.conversation._is_user_nudge_global_limit_blocked(
            self.user)

        assert is_user_blocked == True

    def test_nudge_is_user_global_limit_blocked_respecting_global_limit(self):
        """
        Should return False if user post many comments disrespecting the
        nudge global limits
        """
        self.conversation.comment_nudge_global_limit = 2
        self.create_valid_comment(self.conversation, self.user)
        is_user_blocked = self.conversation._is_user_nudge_global_limit_blocked(
            self.user)

        assert is_user_blocked == False

    def test_nudge_status_should_return_normal(self):
        """
        Should return normal if user is respecting nudge limits and post
        moderately
        """
        self.conversation.comment_nudge_global_limit = 5
        self.conversation.comment_nudge = 4
        self.conversation.comment_nudge_interval = 4
        self.create_valid_comment(self.conversation, self.user)

        nudge_status = self.conversation.get_nudge_status(self.user)

        assert nudge_status == Conversation.NUDGE.normal

    def test_nudge_status_should_return_eager(self):
        """
        Should return eager if user is respecting nudge limits but post too
        many comments in a short time
        """
        self.conversation.comment_nudge_global_limit = 5
        self.conversation.comment_nudge = 4
        self.conversation.comment_nudge_interval = 2
        self.create_valid_comments(2, self.conversation, self.user)

        nudge_status = self.conversation.get_nudge_status(self.user)

        assert nudge_status == Conversation.NUDGE.eager

    def test_nudge_status_should_return_interval_blocked(self):
        """
        Should return interval blocked if user isn't respecting nudge limits
        posting too many comments in a short time
        """
        self.conversation.comment_nudge_global_limit = 5
        self.conversation.comment_nudge = 2
        self.conversation.comment_nudge_interval = 10
        self.create_valid_comments(2, self.conversation, self.user)

        nudge_status = self.conversation.get_nudge_status(self.user)

        assert nudge_status == Conversation.NUDGE.interval_blocked

    def test_nudge_status_should_return_global_blocked(self):
        """
        Should return global blocked post the global limit of comments
        """
        self.conversation.comment_nudge_global_limit = 1
        self.create_valid_comment(self.conversation, self.user)
        nudge_status = self.conversation.get_nudge_status(self.user)

        assert nudge_status == Conversation.NUDGE.global_blocked

    def test_get_random_comment(self):
        """
        Should return a conversation's comment
        """
        comments = self.create_valid_comments(3, self.conversation, self.user)
        random_comment = self.conversation.get_random_unvoted_comment(self.other_user)

        assert random_comment in comments

    def test_get_random_comment_should_return_only_approved_comments(self):
        """
        Should not return rejected or unmoderated comments
        """
        comments = [self.create_valid_comment(self.conversation, self.user, approval)
                    for approval in [Comment.REJECTED, Comment.UNMODERATED]]

        with pytest.raises(Comment.DoesNotExist) as err:
            self.conversation.get_random_unvoted_comment(self.other_user)

    def test_get_random_comment_should_return_only_unvoted_comments(self):
        """
        Should not return any comment because the only one is already voted
        """
        comment = self.create_valid_comment(self.conversation, self.user)
        comment.votes.create(author=self.other_user, value=Vote.AGREE)

        with pytest.raises(Comment.DoesNotExist) as err:
            self.conversation.get_random_unvoted_comment(self.other_user)

    def test_random_comment_should_not_be_of_current_user(self):
        """
        User can't get its own comment
        """
        self.create_valid_comment(self.conversation, self.user)

        with pytest.raises(Comment.DoesNotExist) as err:
            self.conversation.get_random_unvoted_comment(self.user)

    def test_get_user_participation_ratio(self):
        """
        User participation ratio should be the total of user votes divided by
        the total of comments maden by other users
        """
        comment = self.create_valid_comment(self.conversation, self.other_user)
        self.create_valid_comment(self.conversation, self.user)
        comment.votes.create(author=self.user, value=Vote.DISAGREE)

        user_partipation_ratio = self.conversation.get_user_participation_ratio(
            self.user)

        assert user_partipation_ratio == 1.0

    def test_user_participation_ratio_should_be_zero(self):
        """
        If there are no other user's comments, the participation ratio should
        be zero
        """
        user_partipation_ratio = self.conversation.get_user_participation_ratio(
            self.user)

        assert user_partipation_ratio == 0


class TestVote(TestBase):
    def setup(self):
        super(TestVote, self).setup()
        self.comment = self.create_valid_comment(self.conversation, self.user)
        self.vote = self.create_valid_vote(self.comment, self.user)

    def test_unique_vote_per_comment(self):
        self.comment.votes.create(author=self.other_user, value=Vote.AGREE)

        with pytest.raises(IntegrityError) as err:
            self.comment.votes.create(author=self.other_user, value=Vote.AGREE)

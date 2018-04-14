import datetime
import time

import pytest
from django.db.utils import IntegrityError
from django.utils.timezone import make_aware, get_current_timezone

from ej.conversations.models import (
    Conversation,
    Comment,
    Vote,
)
from ej.conversations.models.conversation import get_datetime_interval, \
    get_nudge_interval_comments, is_user_nudge_eager, \
    is_user_nudge_interval_blocked, is_user_nudge_global_limit_blocked
from .helpers import (
    create_valid_comment,
    create_valid_comments,
)

pytestmark = pytest.mark.django_db


class TestConversation:

    def test_create_valid_comment(self, user, conversation: Conversation):
        old_counter = conversation.comments.count()
        create_valid_comment(conversation, user)
        new_counter = conversation.comments.count()

        assert old_counter == 0
        assert new_counter == 1

    def test_nudge_enum_status_codes(self, conversation: Conversation):
        """
        Nudge blocked status should return too many request http status code (429)
        Eager and normal status should return a success http status code (200)
        """
        assert conversation.NUDGE.interval_blocked.value['status_code'] == 429
        assert conversation.NUDGE.global_blocked.value['status_code'] == 429
        assert conversation.NUDGE.eager.value['status_code'] == 201
        assert conversation.NUDGE.normal.value['status_code'] == 201

    def test_nudge_get_datetime_interval(self, conversation: Conversation):
        """
        Time interval should be a datetime.now() past the interval arg
        """
        for interval in [0, 1, 200]:
            now = datetime.datetime.now()
            past = get_datetime_interval(interval, now)
            timediff = make_aware(now, get_current_timezone()) - past
            assert timediff.seconds == interval

    def test_nudge_interval_comments(self, user, conversation: Conversation):
        """
        It should return only comments in specific interval
        """
        conversation.comment_nudge_interval = 1  # seconds
        create_valid_comment(conversation, user)
        time.sleep(2)
        create_valid_comments(2, conversation, user)
        recent_user_comments = get_nudge_interval_comments(conversation, user)

        assert recent_user_comments.count() == 2

    def test_nudge_is_user_eager_with_a_comment(self, user, conversation: Conversation):
        """
        Should return true if user is trying to post too much comments
        """
        conversation.comment_nudge = 2
        conversation.comment_nudge_interval = 2
        create_valid_comment(conversation, user)
        user_comments = get_nudge_interval_comments(conversation, user)

        assert is_user_nudge_eager(conversation, user_comments.count(), user_comments)

    def test_nudge_is_user_eager_with_multiple_comments(self, user, conversation: Conversation):
        """
        Should return true if user is trying to post too much comments
        """
        conversation.comment_nudge = 4
        conversation.comment_nudge_interval = 2
        create_valid_comments(3, conversation, user)
        user_comments = get_nudge_interval_comments(conversation, user)
        assert is_user_nudge_eager(conversation, user_comments.count(), user_comments)

    def test_nudge_is_user_eager_respecting_time_limit(self, user, conversation: Conversation):
        """
        Should return false if user respect the time limit
        """
        conversation.comment_nudge = 4
        conversation.comment_nudge_interval = 2
        create_valid_comment(conversation, user)
        user_comments = get_nudge_interval_comments(conversation, user)

        assert is_user_nudge_eager(conversation, user_comments.count(), user_comments) is False

    def test_nudge_is_user_eager_distributing_comments_in_the_time(self, user, conversation: Conversation):
        """
        Should return false if user respect the total time limit
        """
        conversation.comment_nudge = 4
        conversation.comment_nudge_interval = 1
        create_valid_comment(conversation, user)
        time.sleep(2)
        create_valid_comment(conversation, user)
        user_comments = get_nudge_interval_comments(conversation, user)

        assert is_user_nudge_eager(conversation, user_comments.count(), user_comments) is False

    def test_nudge_is_user_interval_blocked(self, user, conversation: Conversation):
        """
        Should return true if user post too many comments disrescpecting time
        limits
        """
        conversation.comment_nudge = 1
        conversation.comment_nudge_interval = 10
        create_valid_comment(conversation, user)
        user_comments_counter = get_nudge_interval_comments(conversation, user).count()
        assert is_user_nudge_interval_blocked(conversation, user_comments_counter)

    def test_nudge_is_user_interval_blocked_respecting_limits(self, user, conversation: Conversation):
        """
        Should return false if user post comments moderately
        """
        conversation.comment_nudge = 2
        conversation.comment_nudge_interval = 10
        create_valid_comment(conversation, user)
        user_comments_counter = get_nudge_interval_comments(conversation, user).count()
        assert is_user_nudge_interval_blocked(conversation, user_comments_counter) is False

    def test_nudge_is_user_global_limit_blocked(self, user, conversation: Conversation):
        """
        Should return true if user post many comments disrespecting the
        nudge global limits
        """
        conversation.comment_nudge_global_limit = 1
        create_valid_comment(conversation, user)
        assert is_user_nudge_global_limit_blocked(conversation, user)

    def test_nudge_is_user_global_limit_blocked_respecting_global_limit(self, user, conversation: Conversation):
        """
        Should return False if user post many comments disrespecting the
        nudge global limits
        """
        conversation.comment_nudge_global_limit = 2
        create_valid_comment(conversation, user)
        assert not is_user_nudge_global_limit_blocked(conversation, user)

    def test_nudge_status_should_return_normal(self, user, conversation: Conversation):
        """
        Should return normal if user is respecting nudge limits and post
        moderately
        """
        conversation.comment_nudge_global_limit = 5
        conversation.comment_nudge = 4
        conversation.comment_nudge_interval = 4
        create_valid_comment(conversation, user)
        nudge_status = conversation.get_nudge_status(user)
        assert nudge_status == Conversation.NUDGE.normal

    def test_nudge_status_should_return_eager(self, user, conversation: Conversation):
        """
        Should return eager if user is respecting nudge limits but post too
        many comments in a short time
        """
        conversation.comment_nudge_global_limit = 5
        conversation.comment_nudge = 4
        conversation.comment_nudge_interval = 2
        create_valid_comments(3, conversation, user)
        nudge_status = conversation.get_nudge_status(user)
        assert nudge_status == Conversation.NUDGE.eager

    def test_nudge_status_should_return_interval_blocked(self, user, conversation: Conversation):
        """
        Should return interval blocked if user isn't respecting nudge limits
        posting too many comments in a short time
        """
        conversation.comment_nudge_global_limit = 5
        conversation.comment_nudge = 2
        conversation.comment_nudge_interval = 10
        create_valid_comments(2, conversation, user)
        nudge_status = conversation.get_nudge_status(user)

        assert nudge_status == Conversation.NUDGE.interval_blocked

    def test_nudge_status_should_return_global_blocked(self, user, conversation: Conversation):
        """
        Should return global blocked post the global limit of comments
        """
        conversation.comment_nudge_global_limit = 1
        create_valid_comment(conversation, user)
        nudge_status = conversation.get_nudge_status(user)

        assert nudge_status == Conversation.NUDGE.global_blocked

    def test_get_random_comment(self, user, other_user, conversation: Conversation):
        """
        Should return a conversation's comment
        """
        comments = create_valid_comments(3, conversation, user)
        random_comment = conversation.get_random_unvoted_comment(other_user)

        assert random_comment in comments

    def test_get_random_comment_should_return_only_approved_comments(self, user,
                                                                     other_user, conversation: Conversation):
        """
        Should not return rejected or unmoderated comments
        """
        comments = [create_valid_comment(conversation, user, approval)
                    for approval in [Comment.REJECTED, Comment.PENDING]]

        with pytest.raises(Comment.DoesNotExist) as err:
            conversation.get_random_unvoted_comment(other_user)

    def test_get_random_comment_should_return_only_unvoted_comments(self, user,
                                                                    other_user, conversation: Conversation):
        """
        Should not return any comment because the only one is already voted
        """
        comment = create_valid_comment(conversation, user)
        comment.votes.create(author=other_user, value=Vote.AGREE)

        with pytest.raises(Comment.DoesNotExist) as err:
            conversation.get_random_unvoted_comment(other_user)

    def test_random_comment_should_not_be_of_current_user(self, user, conversation: Conversation):
        """
        User can't get its own comment
        """
        create_valid_comment(conversation, user)

        with pytest.raises(Comment.DoesNotExist) as err:
            conversation.get_random_unvoted_comment(user)

    def test_get_user_participation_ratio(self, user, other_user, conversation: Conversation):
        """
        User participation ratio should be the total of user votes divided by
        the total of comments maden by other users
        """
        comment = create_valid_comment(conversation, other_user)
        create_valid_comment(conversation, user)
        comment.votes.create(author=user, value=Vote.DISAGREE)
        user_partipation_ratio = conversation.get_user_participation_ratio(user)

        assert user_partipation_ratio == 1.0

    def test_user_participation_ratio_should_be_zero(self, user, conversation: Conversation):
        """
        If there are no other user's comments, the participation ratio should
        be zero
        """
        user_partipation_ratio = conversation.get_user_participation_ratio(user)
        assert user_partipation_ratio == 0


class TestVote:
    def test_unique_vote_per_comment(self, other_user, comment):
        comment.votes.create(author=other_user, value=Vote.AGREE)

        with pytest.raises(IntegrityError) as err:
            comment.votes.create(author=other_user, value=Vote.AGREE)

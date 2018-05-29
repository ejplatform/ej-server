import pytest
from django.core.exceptions import ValidationError

from ej_conversations import create_conversation
from ej_conversations.models import Vote, Choice


class TestConversation:
    def test_random_comment_invariants(self, db, mk_conversation, mk_user):
        conversation = mk_conversation()
        user = mk_user(username='user')
        other = mk_user(username='other')
        mk_comment = conversation.create_comment
        comments = [
            mk_comment(other, 'a', status='approved', check_limits=False),
            mk_comment(user, 'b', status='approved', check_limits=False),
            mk_comment(other, 'c', status='pending', check_limits=False),
            mk_comment(other, 'd', status='rejected', check_limits=False),
        ]

        cmt = conversation.next_comment(user)
        assert cmt == comments[0]
        assert cmt.status == cmt.STATUS.approved
        assert cmt.author != user
        assert not Vote.objects.filter(author=user, comment=cmt)

    def test_create_conversation(self, user):
        conversation = create_conversation('what?', 'test', user, commit=False)
        assert conversation.author == user


class TestVote:
    def test_unique_vote_per_comment(self, mk_user, comment_db):
        user = mk_user()
        comment_db.vote(user, 'agree')
        with pytest.raises(ValidationError):
            comment_db.vote(user, 'disagree')

    def test_cannot_vote_in_non_moderated_comment(self, comment_db, user_db):
        comment_db.status = comment_db.STATUS.pending

        with pytest.raises(ValidationError):
            comment_db.vote(user_db, 'agree')

    def test_create_vote_happy_paths(self, comment_db, mk_user):
        vote1 = comment_db.vote(mk_user(username='user1'), 'agree')
        vote2 = comment_db.vote(mk_user(username='user2'), Choice.AGREE)
        assert vote1.choice == vote2.choice

    def test_create_vote_unhappy_paths(self, comment_db, user_db):
        with pytest.raises(ValueError):
            comment_db.vote(user_db, 42)

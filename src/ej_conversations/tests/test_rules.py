from ej_conversations.rules import vote_progress_porcentage
from ej_users.models import User
from django.contrib.auth.models import AnonymousUser


class TestVoteProgressPorcentage:
    def test_progress_user(self, conversation, db):
        user = User.objects.create_user('user@server.com', 'password')
        assert vote_progress_porcentage(conversation, user) == 100
        conversation.create_comment(user, 'aa', status='approved', check_limits=False)
        assert vote_progress_porcentage(conversation, user) == 0

    def test_progress_anonymous_user(self, conversation, db):
        user = AnonymousUser()
        assert vote_progress_porcentage(conversation, user) == 0

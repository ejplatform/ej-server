import pytest
from ej_boards import rules
from ej_boards.models import Board
from ej_users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user('name@server.com', '1234', name='name')


class TestBoardRules:
    def test_user_has_board(self, db, user):
        assert not rules.has_board(user)
        Board.objects.create(owner=user, title='title', slug='slug')
        assert rules.has_board(user)

    def test_user_can_add_conversation_in_board(self, db, user):
        board = Board.objects.create(owner=user, title='title', slug='slug')
        assert rules.can_add_conversation(user, board)
        user.limit_board_conversations = 0
        user.save()
        print(rules.conversation_limit(user))
        assert not rules.can_add_conversation(user, board)
        other_user = User.objects.create_user('name@name.com', '123')
        board.owner = other_user
        assert not rules.can_add_conversation(user, board)
        assert rules.can_add_conversation(other_user, board)

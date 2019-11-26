from ej_boards.models import Board
from ej_boards.mommy_recipes import BoardRecipes
from ej_conversations import create_conversation


class TestBoardModel(BoardRecipes):
    def test_str_board(self, db, board):
        assert board.title == str(board)

    def test_get_board_absolute_url(self, db, board):
        assert board.get_absolute_url() == f"/{board.slug}/"

    def test_get_default_palette_css_class(self, db, board):
        from ej_boards.models import Board

        assert Board.css_palette == "bluePalette"

    def test_get_board_palette_css_class(self, db, board):
        board.palette = "Grey"
        assert board.css_palette == "greyPalette"

    def test_get_board_palette_from_conversation(self, mk_conversation, mk_user):
        user = mk_user(email="someuser@mail.com")
        conversation = create_conversation("foo", "conv1", user)
        board = Board.objects.create(slug="board1", owner=user, palette="Orange", description="board")
        board.conversations.add(conversation)
        assert conversation.css_palette == "orangePalette"
        assert conversation.css_light_palette == "orangePalette-light"
        assert conversation.css_text_palette == "orangePalette-text"

    def test_get_board_default_palette_from_conversation(self, mk_user):
        user = mk_user(email="someuser@mail.com")
        conversation = create_conversation("foo", "conv1", user)
        board = Board.objects.create(slug="board1", owner=user, description="board")
        board.conversations.add(conversation)
        assert conversation.css_palette == "bluePalette"

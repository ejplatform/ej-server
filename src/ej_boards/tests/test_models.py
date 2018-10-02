from ej_boards.mommy_recipes import BoardRecipes


class TestBoardModel(BoardRecipes):
    def test_str_board(self, db, board):
        assert board.title == str(board)

    def test_get_board_absolute_url(self, db, board):
        assert board.get_absolute_url() == f'/{board.slug}/'

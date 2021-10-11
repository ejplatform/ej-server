from model_mommy.recipe import Recipe, foreign_key
from sidekick import record

from ej.testing import EjRecipes
from .models import Board

__all__ = ["BoardRecipes"]


class BoardRecipes(EjRecipes):
    board = Recipe(
        Board,
        slug="board-slug",
        title="Title",
        description="Description",
        owner=foreign_key(EjRecipes.user),
    )

    def get_data(self, request):
        data = super().get_data(request)
        board = self.board.make(owner=data.author)
        return record(data, board=board)


BoardRecipes.update_globals(globals())

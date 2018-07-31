from model_mommy.recipe import Recipe, foreign_key

from ej_conversations.mommy_recipes import ConversationRecipes as base
from .models import Board


class BoardRecipes(base):
    board = Recipe(
        Board,
        slug='board-slug',
        title='Title',
        description='Description',
        owner=foreign_key(base.author),
    )


BoardRecipes.update_globals(globals())

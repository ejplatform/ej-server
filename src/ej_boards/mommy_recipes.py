from model_mommy.recipe import Recipe, foreign_key

from ej_conversations.mommy_recipes import ConversationRecipes, author
from .models import Board


class BoardRecipes(ConversationRecipes):
    board = Recipe(
        Board,
        slug='board-slug',
        title='Title',
        description='Description',
        owner=foreign_key(author),
    )


BoardRecipes.update_globals(globals())

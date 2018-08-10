from model_mommy.recipe import Recipe, foreign_key

from ej_conversations.mommy_recipes import ConversationRecipes as Base
from .models import Board


class BoardRecipes(Base):
    board = Recipe(
        Board,
        slug='board-slug',
        title='Title',
        description='Description',
        owner=foreign_key(Base.author),
    )


BoardRecipes.update_globals(globals())

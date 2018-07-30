from model_mommy.recipe import foreign_key

from ej_conversations.mommy_recipes import *
from .models import Board

board = recipe_fixtures(
    Board, 'board',
    slug='board-slug',
    title='Title',
    description='Description',
    owner=foreign_key(author),
)
update_globals(globals())

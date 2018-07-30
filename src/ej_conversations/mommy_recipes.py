from django.contrib.auth import get_user_model as _user_model
from model_mommy.recipe import Recipe, foreign_key as _foreign_key

from .models import Comment, Conversation, Vote, Choice

__all__ = ['user', 'author', 'root', 'conversation', 'comment', 'vote',
           'recipe_fixtures', 'make_fixtures', 'update_globals']

User = _user_model()
user = Recipe(User, is_superuser=False, email='user@domain.com', name='user')
author = Recipe(User, is_superuser=False, email='author@domain.com', name='author')
root = Recipe(User, is_superuser=True, email='root@domain.com', is_staff=True, name='root')
conversation = Recipe(
    Conversation,
    title='Conversation',
    text='question?',
    slug='conversation',
    author=_foreign_key(author),
)
comment = Recipe(
    Comment,
    author=_foreign_key(author.extend(email='comment_author@domain.com')),
    content='comment',
    conversation=conversation.make,
    status=Comment.STATUS.approved,
)
vote = Recipe(
    Vote,
    comment=comment.make,
    author=_foreign_key(author.extend(email='voter@domain.com')),
    choice=Choice.AGREE,
)


def recipe_fixtures(model, name, save=None, **kwargs):
    return make_fixtures(Recipe(model, **kwargs), name, save=save)


def make_fixtures(recipe, name, save=None):
    import pytest

    @pytest.fixture(name=name)
    def fixture_function():
        return recipe.prepare()

    @pytest.fixture(name=name + '_db')
    def fixture_function_db(db):
        return recipe.make()

    @pytest.fixture(name=name + '_recipe')
    def fixture_function_rec():
        return recipe

    @pytest.fixture(name='mk_' + name)
    def fixture_function_mk(db):
        return recipe.make

    if save:
        ns = {
            'fixture_' + name: fixture_function,
            'fixture_' + name + '_db': fixture_function_db,
            'fixture_' + name + '_recipe': fixture_function_rec,
            'fixture_mk_' + name: fixture_function_mk,
        }
        save.update(ns)
        save.get('__all__', []).extend(ns)

    return recipe


def update_globals(glob):
    for k, v in list(glob.items()):
        if isinstance(v, Recipe):
            make_fixtures(v, k, save=glob)


update_globals(globals())

import pytest
from django.contrib.auth import get_user_model
from model_mommy.recipe import Recipe as BaseRecipe

User = get_user_model()


class Recipe(BaseRecipe):
    def dependencies(self):
        return {}

    def get_fixture(self):
        print(self.dependencies())


class FixtureMeta(type):
    def __init__(cls, clsname, bases, ns):
        super().__init__(clsname, bases, ns)
        cls._fixtures = dict(getattr(cls, '_fixtures', {}))
        cls._recipes = dict(getattr(cls, '_recipes', {}))

        for name, recipe in ns.items():
            if isinstance(recipe, Recipe):
                ns = make_recipe(name, recipe)
                for k, v in ns.items():
                    setattr(cls, k, fixture_method(v))
                cls._fixtures.update(ns)
                cls._recipes[name] = recipe

    def update_globals(cls, globals):
        globals.update(cls._fixtures)
        globals.update(cls._recipes)


def make_recipe(name, recipe):
    @pytest.fixture(name=name)
    def fixture_function():
        return recipe.prepare()

    @pytest.fixture(name=name + '_db')
    def fixture_function_db(db):
        return recipe.make()

    @pytest.fixture(name=name + '_rec')
    def fixture_function_rec():
        return recipe

    @pytest.fixture(name='mk_' + name)
    def fixture_function_mk(db):
        return recipe.make

    @pytest.fixture(name='prep_' + name)
    def fixture_function_prep():
        return recipe.prepare

    fixture_map = {
        'fixture_' + name: fixture_function,
        'fixture_' + name + '_db': fixture_function_db,
        'fixture_' + name + '_recipe': fixture_function_rec,
        'fixture_mk_' + name: fixture_function_mk,
        'fixture_prep_' + name: fixture_function_prep,
    }
    recipe.fixture_map = fixture_map
    return fixture_map


def fixture_method(func):
    meta = func._pytestfixturefunction
    name = meta.name
    if name.endswith('_db') or name.startswith('mk_'):
        new = lambda self, db: func(db)
    else:
        new = lambda self: func()
    new._pytestfixturefunction = meta
    return new


class WithRecipes(metaclass=FixtureMeta):
    """
    Base class for all test classes with fixtures.
    """
    base = object()


class EjRecipes(metaclass=FixtureMeta):
    """
    Base recipes for the site
    """
    user = Recipe(User, is_superuser=False, email='user@domain.com', name='user')
    author = Recipe(User, is_superuser=False, email='author@domain.com', name='author')
    root = Recipe(User, is_superuser=True, email='root@domain.com', is_staff=True, name='root')

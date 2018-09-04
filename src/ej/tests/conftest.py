from django.contrib.auth import get_user_model
from model_mommy.recipe import Recipe

__all__ = ['user', 'root']

User = get_user_model()
user = Recipe(User, is_superuser=False, email='user@domain.com')
root = Recipe(User, is_superuser=True, email='root@domain.com', is_staff=True)


def make_fixture(recipe, name):
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

    ns = {}
    ns['fixture_' + name] = fixture_function
    ns['fixture_' + name + '_db'] = fixture_function_db
    ns['fixture_' + name + '_recipe'] = fixture_function_rec
    ns['fixture_mk_' + name] = fixture_function_mk
    globals().update(ns)
    __all__.extend(ns)


[make_fixture(v, k)
 for k, v in list(globals().items())
 if isinstance(v, Recipe)]

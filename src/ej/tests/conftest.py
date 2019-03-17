from django.contrib.auth import get_user_model
from django.test import signals
from jinja2 import Template as Jinja2Template
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

    ns = {
        'fixture_' + name: fixture_function,
        'fixture_' + name + '_db': fixture_function_db,
        'fixture_' + name + '_recipe': fixture_function_rec,
        'fixture_mk_' + name: fixture_function_mk
    }
    globals().update(ns)
    __all__.extend(ns)


[make_fixture(v, k)
 for k, v in list(globals().items())
 if isinstance(v, Recipe)]


#
# Patch Jinja2 to sent template_rendered signal after rendering template
#
def patch_jinja2():
    render = Jinja2Template.render

    def context_render(self, *args, **kwargs):
        context = dict(*args, **kwargs)
        result = render(self, *args, **kwargs)
        signals.template_rendered.send(
            sender=self,
            template=self,
            context=context
        )
        return result

    if not getattr(Jinja2Template, '_render_patch', False):
        Jinja2Template.render = context_render
        Jinja2Template._render_patch = True


patch_jinja2()

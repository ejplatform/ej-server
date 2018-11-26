from model_mommy.recipe import Recipe, foreign_key as _foreign_key

from ej.testing import EjRecipes
from .models import PasswordResetToken

__all__ = ['UserRecipes']


class UserRecipes(EjRecipes):
    token = Recipe(
        PasswordResetToken,
        url='random-data',
        user=_foreign_key(EjRecipes.user),
    )


UserRecipes.update_globals(globals())

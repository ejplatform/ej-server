from model_mommy.recipe import Recipe, foreign_key as _foreign_key
from sidekick import record

from ej.testing import EjRecipes
from .models import PasswordResetToken

__all__ = ["UserRecipes"]


class UserRecipes(EjRecipes):
    token = Recipe(PasswordResetToken, url="random-data", user=_foreign_key(EjRecipes.user))

    def get_data(self, request):
        data = super().get_data(request)
        return record(data, token=self.token.make(user=data.user))


UserRecipes.update_globals(globals())

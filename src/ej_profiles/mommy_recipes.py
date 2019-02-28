import pytest
from model_mommy.recipe import Recipe
from sidekick import record

from ej.testing import EjRecipes
from .models import Profile


class ProfileRecipes(EjRecipes):
    profile = Recipe(Profile)

    def get_data(self, request):
        data = super().get_data(request)
        profile = self.profile.make(user=data.user)
        return record(data, profile=profile)

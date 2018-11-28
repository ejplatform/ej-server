import pytest
from model_mommy.recipe import Recipe
from sidekick import record

from ej.testing import EjRecipes
from .models import Profile


class ProfileRecipes(EjRecipes):
    profile = Recipe(Profile)

    @pytest.fixture
    def data(self, request):
        data = super().data(request)
        profile = self.profile.make(user=data.user)
        return record(data, profile=profile)

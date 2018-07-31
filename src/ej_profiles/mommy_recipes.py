from ej.testing import EjRecipes as base
from model_mommy.recipe import foreign_key, related, Recipe


class ProfileRecipes(base):
    profile = Recipe()

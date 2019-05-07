import pytest
from model_mommy.recipe import Recipe, foreign_key

from ej_conversations.mommy_recipes import ConversationRecipes
from .models import GivenBridgePower, GivenMinorityPower, CommentPromotion

__all__ = ["PowerRecipes"]

recipe = ConversationRecipes
_power_kwargs = dict(
    user=foreign_key(recipe.user.extend(email="has-power@domain.com")),
    conversation=foreign_key(recipe.conversation),
)


class PowerRecipes(ConversationRecipes):
    given_bridge_power = Recipe(GivenBridgePower, **_power_kwargs)
    given_minority_power = Recipe(GivenMinorityPower, **_power_kwargs)
    comment_promotion = Recipe(
        CommentPromotion,
        comment=foreign_key(recipe.comment),
        promoter=foreign_key(recipe.author.extend(email="comment_promoter@domain.com")),
    )

    @pytest.fixture
    def data(self, request):
        data = super().data(request)
        return data


PowerRecipes.update_globals(globals())

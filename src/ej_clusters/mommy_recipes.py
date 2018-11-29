import pytest
from model_mommy.recipe import Recipe, foreign_key as _foreign_key
from sidekick import record

from ej.testing import EjRecipes
from ej_conversations.models import Choice
from ej_conversations.mommy_recipes import ConversationRecipes
from .models import Stereotype, StereotypeVote

__all__ = ['ClustersRecipes']


class ClustersRecipes(EjRecipes):
    stereotype = Recipe(
        Stereotype,
        name='Stereotypeone',
        description='description?',
        conversation=_foreign_key(ConversationRecipes.conversation),
    )
    stereotype_vote = Recipe(
        StereotypeVote,
        author=stereotype.make,
        choice=Choice.AGREE,
        comment=_foreign_key(ConversationRecipes.comment)
    )

    @pytest.fixture
    def data(self, request):
        data = super().data(request)
        stereotype = self.stereotype.make(conversation=data.conversation)
        votes = [
            self.stereotype_vote.make(author=stereotype, comment=comment)
            for comment in data.comments
        ]
        return record(data, stereotype=stereotype, stereotype_votes=votes)


ClustersRecipes.update_globals(globals())

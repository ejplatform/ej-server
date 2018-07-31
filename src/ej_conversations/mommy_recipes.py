from model_mommy.recipe import Recipe, foreign_key as _foreign_key

from ej.testing import EjRecipes
from .models import Comment, Conversation, Vote, Choice

__all__ = ['ConversationRecipes']


class ConversationRecipes(EjRecipes):
    conversation = Recipe(
        Conversation,
        title='Conversation',
        text='question?',
        slug='conversation',
        author=_foreign_key(EjRecipes.author),
    )
    comment = Recipe(
        Comment,
        author=_foreign_key(EjRecipes.author.extend(email='comment_author@domain.com')),
        content='comment',
        conversation=conversation.make,
        status=Comment.STATUS.approved,
    )
    vote = Recipe(
        Vote,
        comment=comment.make,
        author=_foreign_key(EjRecipes.author.extend(email='voter@domain.com')),
        choice=Choice.AGREE,
    )


ConversationRecipes.update_globals(globals())

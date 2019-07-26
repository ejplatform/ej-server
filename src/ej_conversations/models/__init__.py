from .comment import Comment
from .comment_queryset import CommentQuerySet
from .conversation import Conversation, FavoriteConversation, ConversationTag
from .conversation_queryset import ConversationQuerySet
from .vote import Vote, normalize_choice
from .vote_queryset import VoteQuerySet
from ..enums import Choice

#
# Exposed default managers
#
comments = Comment.approved
conversations = Conversation.objects.filter(is_hidden=False)
votes = Vote.objects


#
# Patch other models
#
def _patch():
    from django.contrib.auth import get_user_model
    from sidekick import lazy, property, placeholder as _

    #
    # Patch user model
    #
    user = get_user_model()

    # Enhanced querysets
    user.approved_comments = property(_.comments.approved())
    user.n_rejected_comments = property(_.comments.rejected())

    # Statistics
    user.n_conversations = lazy(_.conversations.count())
    user.n_comments = lazy(_.approved_comments.count())
    user.n_rejected_comments = lazy(_.rejected_comments.count())
    user.n_votes = lazy(_.votes.count())
    user.n_final_votes = lazy(_.votes.exclude(choice=Choice.SKIP).count())


_patch()

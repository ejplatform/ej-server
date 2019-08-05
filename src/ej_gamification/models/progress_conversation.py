from boogie import models
from django.utils.translation import ugettext_lazy as _, ugettext as __
from sidekick import delegate_to, lazy

from .progress_base import ProgressBase, signals
from .progress_queryset import ProgressQuerySet
from ..enums import ConversationLevel, CommenterLevel
from ..utils import compute_points


class ConversationProgress(ProgressBase):
    """
    Tracks activity in conversation.
    """

    conversation = models.OneToOneField(
        "ej_conversations.Conversation", related_name="progress", on_delete=models.CASCADE
    )
    conversation_level = models.EnumField(
        ConversationLevel,
        default=CommenterLevel.NONE,
        verbose_name=_("conversation level"),
        help_text=_("Measures the level of engagement for conversation."),
    )
    max_conversation_level = models.EnumField(
        ConversationLevel,
        default=CommenterLevel.NONE,
        editable=False,
        help_text=_("maximum achieved conversation level"),
    )

    # Non de-normalized fields: conversations
    n_final_votes = delegate_to("conversation")
    n_approved_comments = delegate_to("conversation")
    n_rejected_comments = delegate_to("conversation")
    n_participants = delegate_to("conversation")
    n_favorites = delegate_to("conversation")
    n_tags = delegate_to("conversation")

    # Clusterization
    n_clusters = delegate_to("conversation")
    n_stereotypes = delegate_to("conversation")

    # Gamification
    n_endorsements = delegate_to("conversation")

    # Signals
    level_achievement_signal = lazy(lambda _: signals.conversation_level_achieved, shared=True)

    # Points
    VOTE_POINTS = 1
    APPROVED_COMMENT_POINTS = 2
    REJECTED_COMMENT_POINTS = -0.125
    ENDORSEMENT_POINTS = 3

    pts_final_votes = compute_points(1)
    pts_approved_comments = compute_points(2)
    pts_rejected_comments = compute_points(-0.125)
    pts_endorsements = compute_points(3)

    objects = ProgressQuerySet.as_manager()

    class Meta:
        verbose_name = _("Conversation score")
        verbose_name_plural = _("Conversation scores")

    def __str__(self):
        return __('Progress for "{conversation}"').format(conversation=self.conversation)

    def compute_score(self):
        """
        Compute the total number of points for user contribution.

        Conversation score is based on the following rules:
            * Vote: 1 points
            * Accepted comment: 2 points
            * Rejected comment: -3 points
            * Endorsement created: 3 points

        Returns:
            Total score (int)
        """
        return int(
            max(
                0,
                self.score_bias
                + self.pts_final_votes
                + self.pts_approved_comments
                + self.pts_rejected_comments
                + self.pts_endorsements,
            )
        )

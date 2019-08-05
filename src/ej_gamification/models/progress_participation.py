from boogie import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext as __
from sidekick import lazy, delegate_to, placeholder as this

from ej_conversations import Choice
from .progress_base import ProgressBase, signals
from .progress_queryset import ProgressQuerySet
from ..enums import VoterLevel
from ..utils import compute_points


class ParticipationProgress(ProgressBase):
    """
    Tracks user evolution in conversation.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="participation_progresses",
        on_delete=models.CASCADE,
        editable=False,
    )
    conversation = models.ForeignKey(
        "ej_conversations.Conversation",
        related_name="participation_progresses",
        on_delete=models.CASCADE,
        editable=False,
    )
    voter_level = models.EnumField(
        VoterLevel,
        default=VoterLevel.NONE,
        verbose_name=_("voter level"),
        help_text=_("Measure how many votes user has given in conversation"),
    )
    max_voter_level = models.EnumField(
        VoterLevel, default=VoterLevel.NONE, editable=False, verbose_name=_("maximum achieved voter level")
    )
    is_owner = models.BooleanField(
        _("owner?"),
        default=False,
        help_text=_("Total score is computed differently if user owns conversation."),
    )
    is_focused = models.BooleanField(
        _("focused?"),
        default=False,
        help_text=_("User received a focused badge (i.e., voted on all comments)"),
    )

    # Non de-normalized fields: conversations
    is_favorite = lazy(lambda p: p.conversation.favorites.filter(user=p.user).exists())
    n_final_votes = lazy(
        lambda p: p.user.votes.filter(comment__conversation=p.conversation)
        .exclude(choice=Choice.SKIP)
        .count()
    )
    n_approved_comments = lazy(
        lambda p: p.user.approved_comments.filter(conversation=p.conversation).count()
    )
    n_rejected_comments = lazy(
        lambda p: p.user.rejected_comments.filter(conversation=p.conversation).count()
    )
    n_conversation_comments = delegate_to("conversation", name="n_approved_comments")
    n_conversation_approved_comments = delegate_to("conversation", name="n_approved_comments")
    n_conversation_rejected_comments = delegate_to("conversation", name="n_rejected_comments")
    votes_ratio = lazy(this.n_final_votes / (this.n_conversation_comments + 1e-50))

    # Gamification
    # n_endorsements = lazy(lambda p: Endorsement.objects.filter(comment__author=p.user).count())
    # n_given_opinion_bridge_powers = delegate_to('user')
    # n_given_minority_activist_powers = delegate_to('user')
    n_endorsements = 0
    n_given_opinion_bridge_powers = 0
    n_given_minority_activist_powers = 0

    # Points
    VOTE_POINTS = 10
    APPROVED_COMMENT_POINTS = 30
    REJECTED_COMMENT_POINTS = -15
    ENDORSEMENT_POINTS = 15
    OPINION_BRIDGE_POINTS = 50
    MINORITY_ACTIVIST_POINTS = 50
    IS_FOCUSED_POINTS = 50

    pts_final_votes = compute_points(VOTE_POINTS)
    pts_approved_comments = compute_points(APPROVED_COMMENT_POINTS)
    pts_rejected_comments = compute_points(REJECTED_COMMENT_POINTS)
    pts_endorsements = compute_points(ENDORSEMENT_POINTS)
    pts_given_opinion_bridge_powers = compute_points(OPINION_BRIDGE_POINTS)
    pts_given_minority_activist_powers = compute_points(MINORITY_ACTIVIST_POINTS)
    pts_is_focused = compute_points(IS_FOCUSED_POINTS, name="is_focused")

    # Leaderboard
    @lazy
    def n_conversation_scores(self):
        db = ParticipationProgress.objects
        return db.filter(conversation=self.conversation).count()

    @lazy
    def n_higher_scores(self):
        db = ParticipationProgress.objects
        return db.filter(conversation=self.conversation, score__gt=self.score).count()

    n_lower_scores = lazy(this.n_conversation_scores - this.n_higher_scores)

    # Signals
    level_achievement_signal = lazy(lambda _: signals.participation_level_achieved, shared=True)

    objects = ProgressQuerySet.as_manager()

    class Meta:
        verbose_name = _("User score (per conversation)")
        verbose_name_plural = _("User scores (per conversation)")

    def __str__(self):
        msg = __("Progress for user: {user} at {conversation}")
        return msg.format(user=self.user, conversation=self.conversation)

    def sync(self):
        self.is_owner = self.conversation.author == self.user

        # You cannot receive a focused achievement in your own conversation!
        if not self.is_owner:
            n_comments = self.conversation.n_approved_comments
            self.is_focused = (self.n_final_votes >= 20) and (n_comments == self.n_final_votes)

        return super().sync()

    def compute_score(self):
        """
        Compute the total number of points earned by user.

        User score is based on the following rules:
            * Vote: 10 points
            * Accepted comment: 30 points
            * Rejected comment: -30 points
            * Endorsement received: 15 points
            * Opinion bridge: 50 points
            * Minority activist: 50 points
            * Plus the total score of created conversations.
            * Got a focused badge: 50 points.

        Observation:
            Owner do not receive any points for its own conversations

        Returns:
            Total score (int)
        """
        return max(
            0,
            self.score_bias
            + self.pts_final_votes
            + self.pts_approved_comments
            + self.pts_rejected_comments
            + self.pts_endorsements
            + self.pts_given_opinion_bridge_powers
            + self.pts_given_minority_activist_powers
            + self.pts_is_focused,
        )

from boogie import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from sidekick import delegate_to, lazy

from ej_conversations.models import Vote, Comment
from .progress_base import ProgressBase, signals
from .progress_queryset import ProgressQuerySet
from ..enums import CommenterLevel, HostLevel, ProfileLevel, ConversationLevel, ScoreLevel, VoterLevel
from ..utils import compute_points


class UserProgress(ProgressBase):
    """
    Tracks global user evolution.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name="progress", on_delete=models.CASCADE, editable=False
    )
    commenter_level = models.EnumField(
        CommenterLevel,
        default=CommenterLevel.NONE,
        verbose_name=_("commenter level"),
        help_text=_("Measures how much user participated by contributing comments to conversations"),
    )
    max_commenter_level = models.EnumField(
        CommenterLevel,
        default=CommenterLevel.NONE,
        editable=False,
        verbose_name=_("maximum achieved commenter level"),
    )
    host_level = models.EnumField(
        HostLevel,
        default=HostLevel.NONE,
        verbose_name=_("host level"),
        help_text=_("Measures how much user participated by creating engaging conversations."),
    )
    max_host_level = models.EnumField(
        HostLevel, default=HostLevel.NONE, editable=False, verbose_name=_("maximum achieved host level")
    )
    profile_level = models.EnumField(
        ProfileLevel,
        default=ProfileLevel.NONE,
        verbose_name=_("profile level"),
        help_text=_("Measures how complete is the user profile."),
    )
    max_profile_level = models.EnumField(
        ProfileLevel,
        default=ProfileLevel.NONE,
        editable=False,
        verbose_name=_("maximum achieved profile level"),
    )

    # Non de-normalized fields: conversations app
    n_conversations = delegate_to("user")
    n_pending_comments = delegate_to("user")
    n_rejected_comments = delegate_to("user")

    @lazy
    def n_final_votes(self):
        return (
            Vote.objects.filter(author=self.user).exclude(comment__conversation__author=self.user).count()
        )

    @lazy
    def n_approved_comments(self):
        return Comment.objects.filter(author=self.user).exclude(conversation__author=self.user).count()

    # Gamification app
    n_endorsements = 0  # FIXME: delegate_to("user")
    n_given_opinion_bridge_powers = delegate_to("user")
    n_given_minority_activist_powers = delegate_to("user")

    # Level of conversations
    def _conversation_level_checker(*args):
        *_, lvl = args  # ugly trick to make static analysis happy
        return lazy(lambda p: p.user.conversations.filter(progress__conversation_level__gte=lvl).count())

    def _participation_level_checker(*args):
        *_, lvl = args  # ugly trick to make static analysis happy
        return lazy(lambda p: p.user.participation_progresses.filter(voter_level__gte=lvl).count())

    n_conversation_lvl_1 = _conversation_level_checker(ConversationLevel.CONVERSATION_LVL1)
    n_conversation_lvl_2 = _conversation_level_checker(ConversationLevel.CONVERSATION_LVL2)
    n_conversation_lvl_3 = _conversation_level_checker(ConversationLevel.CONVERSATION_LVL3)
    n_conversation_lvl_4 = _conversation_level_checker(ConversationLevel.CONVERSATION_LVL2)
    n_participation_lvl_1 = _participation_level_checker(VoterLevel.VOTER_LVL1)
    n_participation_lvl_2 = _participation_level_checker(VoterLevel.VOTER_LVL2)
    n_participation_lvl_3 = _participation_level_checker(VoterLevel.VOTER_LVL3)
    n_participation_lvl_4 = _participation_level_checker(VoterLevel.VOTER_LVL4)

    del _conversation_level_checker
    del _participation_level_checker

    # Aggregators
    total_conversation_score = delegate_to("user")
    total_participation_score = delegate_to("user")

    # Score points
    VOTE_POINTS = 10
    APPROVED_COMMENT_POINTS = 30
    REJECTED_COMMENT_POINTS = -15
    ENDORSEMENT_POINTS = 15
    OPINION_BRIDGE_POINTS = 50
    MINORITY_ACTIVIST_POINTS = 50

    pts_final_votes = compute_points(VOTE_POINTS)
    pts_approved_comments = compute_points(APPROVED_COMMENT_POINTS)
    pts_rejected_comments = compute_points(REJECTED_COMMENT_POINTS)
    pts_endorsements = compute_points(ENDORSEMENT_POINTS)
    pts_given_opinion_bridge_powers = compute_points(OPINION_BRIDGE_POINTS)
    pts_given_minority_activist_powers = compute_points(MINORITY_ACTIVIST_POINTS)

    # Signals
    level_achievement_signal = lazy(lambda _: signals.user_level_achieved, shared=True)

    score_level = property(lambda self: ScoreLevel.from_score(self.score))

    @property
    def n_trophies(self):
        n = 0
        n += bool(self.score_level)
        n += bool(self.profile_level)
        n += bool(self.host_level)
        n += bool(self.commenter_level)
        n += self.n_conversation_lvl_1
        n += self.n_participation_lvl_1
        return n

    objects = ProgressQuerySet.as_manager()

    class Meta:
        verbose_name = _("User score")
        verbose_name_plural = _("User scores")

    def __str__(self):
        return str(self.user)

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
            + self.total_conversation_score,
        )

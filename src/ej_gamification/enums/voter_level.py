from collections import namedtuple
from math import ceil

from boogie.fields import IntEnum
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ngettext

from ._base import LevelMixin

VoterLevelConfig = namedtuple("VoterLevelConfig", ["votes", "ratio", "votes_sure"])
VOTER_LEVELS = getattr(
    settings,
    "EJ_GAMIFICATION_VOTER_LEVELS",
    [_("Curious"), _("Participative"), _("Dedicated"), _("Militant")],
)


class VoterLevel(LevelMixin, IntEnum):
    """
    VOTER TRACK

    Keeps track of user participation on each conversation.

    The test function receives an instance of ParticipationProgress.
    """

    NONE = 0, _("No level")
    VOTER_LVL1 = 1, VOTER_LEVELS[0]
    VOTER_LVL2 = 2, VOTER_LEVELS[1]
    VOTER_LVL3 = 3, VOTER_LEVELS[2]
    VOTER_LVL4 = 4, VOTER_LEVELS[3]
    comment_bonus = property(lambda self: int(self))

    # Must be a staticmethod because we can't access values directly from the
    # class and if it was a simple list instance, it would become a valid enum
    # value, which we don't want.
    @staticmethod
    def _ranges():
        # m: minimum number of votes
        # r: minimum ratio between number of votes and number of comments
        # n: number of votes that yields level, even if r is not enough
        return (
            VoterLevelConfig(votes=5, ratio=0.10, votes_sure=10),
            VoterLevelConfig(votes=10, ratio=0.25, votes_sure=25),
            VoterLevelConfig(votes=25, ratio=0.50, votes_sure=75),
            VoterLevelConfig(votes=50, ratio=0.99, votes_sure=250),
        )

    @classmethod
    def check_level(cls, obj):
        result = cls.NONE
        votes = obj.n_final_votes
        ratio = obj.votes_ratio

        for level, (m, r, n) in zip(cls.skipping_none(), cls._ranges()):
            if votes < n and (votes < m or ratio < r):
                break
            else:
                result = level
        return result

    def achieve_next_level_msg(self, obj):
        # Special cases
        if self == self.VOTER_LVL4:
            return _("Congratulations! You already achieved the maximum participation level.")

        # Now we compute how many votes are necessary to progress
        votes = obj.n_final_votes
        m, r, n = self._ranges()[self]
        if votes == obj.n_conversation_comments:
            msg = _("You cannot progress unless conversation has at least {n} comments :-(")
            return msg.format(n=m)

        delta = float("inf")
        delta_ = ceil((r - obj.votes_ratio) * obj.n_conversation_comments)
        delta_ = max(delta_, m - votes)
        delta = min(delta_, delta)
        delta = min(delta, n - votes)
        return ngettext(
            "You are only one vote short of advancing to the next level!",
            "You need to cast {n} more votes to advance to the next level!",
            delta,
        ).format(n=delta)

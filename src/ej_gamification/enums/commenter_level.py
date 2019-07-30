from math import ceil

from boogie.fields import IntEnum
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ._base import LevelMixin

COMMENTER_LEVELS = getattr(
    settings, "EJ_GAMIFICATION_COMMENTER_LEVELS", [_("Shy"), _("Up front"), _("Outspoken"), _("Articulate")]
)


class CommenterLevel(LevelMixin, IntEnum):
    """
    COMMENTER TRACK

    Keeps track of the total number of accepted comments. User generally have
    to participate in many different conversation to achieve higher ranks in
    this track.

    The test function receives an instance of UserProgress.
    """

    NONE = 0, _("No level")
    COMMENTER_LVL1 = 1, COMMENTER_LEVELS[0]
    COMMENTER_LVL2 = 2, COMMENTER_LEVELS[1]
    COMMENTER_LVL3 = 3, COMMENTER_LEVELS[2]
    COMMENTER_LVL4 = 4, COMMENTER_LEVELS[3]

    @classmethod
    def _levels(cls):
        return [5, 15, 45, 150]

    @classmethod
    def score(cls, data):
        n = data.n_approved_comments
        m = data.n_endorsements
        return n + m / 2

    @classmethod
    def check_level(cls, data):
        score = cls.score(data)
        level = cls.NONE
        for lvl, points in zip(cls.skipping_none(), cls._levels()):
            if score >= points:
                level = lvl
        return level

    def achieve_next_level_msg(self, data):
        if self == self.COMMENTER_LVL4:
            return _("Congrats! You are at maximum level")
        required_score = self._levels()[self.value] - self.score(data)
        n = ceil(required_score)
        m = ceil(2 * required_score)
        msg = _("You need to publish {n} new comments to upgrade")
        return msg.format(n=n, m=m)

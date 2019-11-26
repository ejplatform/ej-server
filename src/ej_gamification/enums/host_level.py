from boogie.fields import IntEnum
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ngettext

from ._base import LevelMixin

HOST_LEVELS = getattr(
    settings, "EJ_GAMIFICATION_HOST_LEVELS", [_("Cheerful"), _("Leader"), _("Influencer"), _("Authority")]
)


class HostLevel(LevelMixin, IntEnum):
    """
    HOST TRACK

    Keeps track of relevant conversations created by user. Users evolve in this
    track by having created conversations achieving good scores in their
    respective host level tracks.

    The test function receives an instance of UserProgress.
    """

    NONE = 0, _("No level")
    HOST_LVL1 = 1, HOST_LEVELS[0]
    HOST_LVL2 = 2, HOST_LEVELS[1]
    HOST_LVL3 = 3, HOST_LEVELS[2]
    HOST_LVL4 = 4, HOST_LEVELS[3]

    @classmethod
    def _levels(cls):
        return [(2, 0, 0, 0), (4, 2, 0, 0), (8, 3, 1, 0), (16, 8, 3, 1)]

    @classmethod
    def check_level(cls, data):
        level = cls.NONE
        for lvl, (a, b, c, d) in zip(cls.skipping_none(), cls._levels()):
            lvl4 = data.n_conversation_lvl_4
            lvl3 = data.n_conversation_lvl_3
            lvl2 = data.n_conversation_lvl_2
            lvl1 = data.n_conversation_lvl_1
            if lvl4 >= d and lvl3 >= c and lvl2 >= b and lvl1 >= a:
                level = lvl
        return level

    def achieve_next_level_msg(self, data):
        if self is self.HOST_LVL4:
            return _("Congratulations! You reached the maximum level")

        a, b, c, d = self._levels()[self.value]
        msg = lambda n, level: ngettext(
            "You need at least one more conversation at {level}!",
            "You need at least {n} {level} conversations.",
            n,
        ).format(n=n, level=level)

        for n in [4, 3, 2, 1]:
            lvl = getattr(data, f"n_conversation_lvl_{n}")
            if d and d > lvl:
                return msg(d - lvl, _("level {n}").format(n=n))
        return msg(1, _("level 1"))

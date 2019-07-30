from math import sqrt

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

SCORE_LEVELS = getattr(
    settings,
    "EJ_GAMIFICATION_SCORE_LEVELS",
    [_("Beginner"), _("Intermediate"), _("Experienced"), _("Professional"), _("Master")],
)


class ScoreLevel(int):
    """
    A enum-like level integer
    """

    LEVEL_NAMES = (
        (5, SCORE_LEVELS[0]),
        (10, SCORE_LEVELS[1]),
        (20, SCORE_LEVELS[2]),
        (30, SCORE_LEVELS[3]),
        (40, SCORE_LEVELS[4]),
    )

    def __str__(self):
        for max_lvl, name in self.LEVEL_NAMES:
            if max_lvl >= self:
                return str(name)
        return str(_("Ultimate Master"))

    @classmethod
    def check_level(cls, progress):
        """
        Compute level from score.
        """
        return cls.from_score(progress.score)

    @classmethod
    def from_score(cls, score):
        if score < 1000:
            return cls(score / 100)
        else:
            return cls(10 + sqrt((score - 1000) / 100))

    def score_value(self):
        if self <= 10:
            return self * 100
        return 1000 + 100 * (self - 10) ** 2

    def achieve_next_level_msg(self, progress):
        delta_score = ScoreLevel(self + 1).score_value() - progress.score
        return _("You need {n} more points to upgrade.").format(n=delta_score)

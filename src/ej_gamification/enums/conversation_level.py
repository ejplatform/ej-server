from boogie.fields import IntEnum
from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ngettext

from ._base import LevelMixin

CONVERSATION_LEVELS = getattr(
    settings,
    "EJ_GAMIFICATION_CONVERSATION_LEVELS",
    [_("Alive"), _("Engaging"), _("Agitating"), _("Intense")],
)


class ConversationLevel(LevelMixin, IntEnum):
    """
    CONVERSATION TRACK

    Track total participation in a conversation.

    The test function receives an instance of ConversationProgress.
    """

    NONE = 0, _("No level")
    CONVERSATION_LVL1 = 1, CONVERSATION_LEVELS[0]
    CONVERSATION_LVL2 = 2, CONVERSATION_LEVELS[1]
    CONVERSATION_LVL3 = 3, CONVERSATION_LEVELS[2]
    CONVERSATION_LVL4 = 4, CONVERSATION_LEVELS[3]

    @staticmethod
    def _levels():
        return 50, 500, 5000, 50000

    @classmethod
    def check_level(cls, obj):
        result = cls.NONE
        for level, score in zip(cls.skipping_none(), cls._levels()):
            if obj.score >= score:
                result = level
            else:
                break
        return result

    def achieve_next_level_msg(self, obj):
        for level, score in zip(type(self), self._levels()):
            if score > obj.score:
                return ngettext(
                    "Conversation needs only a single point to upgrade!",
                    "Conversation needs a score of at least {n} points, but it has {m}.",
                    score,
                ).format(n=score, m=obj.score)
        return _("Conversation already achieved the maximum level.")

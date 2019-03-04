from django.utils.translation import ugettext_lazy as _

from boogie.fields import IntEnum


class RejectionReason(IntEnum):
    """
    Possible rejection reasons for a comment.
    """
    INCOMPLETE_TEXT = (0, _('Incomplete or incomprehensible text'))
    OFF_TOPIC = (1, _('Off-topic'))
    OFFENSIVE_LANGUAGE = (2, _('Offensive content or language'))
    DUPLICATED_COMMENT = (3, _('Duplicated content'))
    VIOLATE_TERMS_OF_SERVICE = (4, _('Violates terms of service of the platform'))


class Choice(IntEnum):
    """
    Options for a user vote.
    """
    SKIP = 0, _('Skip')
    AGREE = 1, _('Agree')
    DISAGREE = -1, _('Disagree')

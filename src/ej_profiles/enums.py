from django.utils.translation import ugettext_lazy as _

from boogie.fields import IntEnum


class Race(IntEnum):
    NOT_FILLED = 0, _('Not filled')
    BLACK = 1, _('Black')
    BROWN = 2, _('Brown')
    WHITE = 3, _('White')
    YELLOW = 4, _('Yellow')
    INDIGENOUS = 5, _('Indigenous')
    DO_NOT_KNOW = 6, _('Do not know')
    UNDECLARED = 7, _('Not declared')


class Gender(IntEnum):
    NOT_FILLED = 0, _('Not filled')
    FEMALE = 1, _('Female')
    MALE = 2, _('Male')
    OTHER = 20, _('Other')
    UNDECLARED = 21, _('Not declared')

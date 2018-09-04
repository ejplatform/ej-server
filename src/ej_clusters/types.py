from django.utils.translation import ugettext as _

from boogie.fields import IntEnum


class ClusterStatus(IntEnum):
    PENDING_DATA = 0, _('Waiting for more data')
    ACTIVE = 1, _('Active')
    DISABLED = 2, _('Disabled')

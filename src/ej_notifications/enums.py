from django.utils.translation import ugettext_lazy as _

from boogie.fields import IntEnum


class Purpose(IntEnum):
    GENERAL = 0, _('General')
    CONVERSATION = 1, _('Conversation')
    GROUP = 2, _('Group')
    TROPHIES = 3, _('Trophies')
    ADMIN = 4, _('Admin')
    APPROVED_NOTIFICATIONS = 5, _('Approved Notifications')
    DISAPPROVED_NOTIFICATIONS = 6, _('Disapproved Notifications')


class NotificationMode(IntEnum):
    ENABLED = 0, _('Enabled')
    DISABLED = 1, _('Disabled')
    PUSH_NOTIFICATIONS = 3, _('Push notifications')

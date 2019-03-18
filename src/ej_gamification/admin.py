from django.contrib import admin
from django.utils.translation import ugettext as _

from ej_conversations.admin import ConversationAdmin, descr
from . import models
from ej_gamification.models.progress import get_progress

# admin.site.register(models.GivenMinorityPower)
# admin.site.register(models.GivenBridgePower)
admin.site.register(models.Endorsement)
admin.site.register(models.UserProgress)
admin.site.register(models.ConversationProgress)
admin.site.register(models.ParticipationProgress)


#
# Extend conversation admin
#
@descr(_('Recalculate progress for conversation'))
def compute_progress(admin, request, queryset):
    n = 0
    for conversation in queryset:
        get_progress(conversation, sync=True)
        n += 1
    admin.message_user(request, _('{n} values updated.').format(n=n))


ConversationAdmin.actions.extend([compute_progress])

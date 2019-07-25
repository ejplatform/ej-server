from django.contrib import admin
from django.utils.translation import ugettext as _

from ej_conversations.admin import ConversationAdmin, descr
from ej_gamification.models.progress import get_progress
from . import models


# admin.site.register(models.GivenMinorityPower)
# admin.site.register(models.GivenBridgePower)
# admin.site.register(models.Endorsement)


#
# Abstract classes
#
class RecomputableScoresAdmin(admin.ModelAdmin):
    actions = ["recompute_scores"]

    @descr(_("Recompute scores"))
    def recompute_scores(self, request, queryset):
        synced = 0
        for score in queryset:
            score.sync_and_save()
            synced += 1
        self.message_user(request, _("{n} values updated.").format(n=synced))


class UserWithNameAdmin(admin.ModelAdmin):
    list_display = ["user", "user_name"]

    @descr(_("Name"))
    def user_name(self, obj):
        return obj.user.get_full_name()


#
# Concrete classes
#
@admin.register(models.UserProgress)
class UserProgressAdmin(UserWithNameAdmin, RecomputableScoresAdmin):
    list_display = ["user", "user_name", "commenter_level", "host_level", "profile_level", "score"]
    list_filter = ["commenter_level", "host_level", "profile_level"]


@admin.register(models.ParticipationProgress)
class ParticipationProgressAdmin(UserWithNameAdmin, RecomputableScoresAdmin):
    list_display = ["conversation", "user", "user_name", "voter_level", "is_owner", "is_focused", "score"]
    list_filter = ["voter_level", "is_owner", "is_focused"]


@admin.register(models.ConversationProgress)
class ConversationProgressAdmin(RecomputableScoresAdmin):
    list_display = ["conversation", "author", "author_name", "conversation_level", "score"]
    list_filter = ["conversation_level"]

    def author(self, obj):
        return obj.conversation.author.email

    def author_name(self, obj):
        return obj.conversation.author.get_full_name()


#
# Extend conversation admin
#
@descr(_("Recalculate progress for conversation"))
def compute_progress(admin, request, queryset):
    n = 0
    for conversation in queryset:
        get_progress(conversation, sync=True)
        n += 1
    admin.message_user(request, _("{n} values updated.").format(n=n))


ConversationAdmin.actions.extend([compute_progress])

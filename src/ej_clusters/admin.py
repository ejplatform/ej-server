from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from ej_conversations.admin import descr
from . import models


class StereotypeVoteInline(admin.TabularInline):
    model = models.StereotypeVote
    extra = 3


@admin.register(models.Stereotype)
class StereotypeAdmin(admin.ModelAdmin):
    inlines = [StereotypeVoteInline]


class ClusterInline(admin.StackedInline):
    model = models.Cluster
    extra = 1


@admin.register(models.Clusterization)
class ClusterizationManagerAdmin(admin.ModelAdmin):
    inlines = [ClusterInline]
    actions = ["force_clusterization", "update_clusterization"]

    @descr(_("Force clusterization (slow)"))
    def force_clusterization(self, request, queryset, force=True):
        for clusterization in queryset:
            clusterization.update_clusterization(force=force)
        self.message_user(request, _("Clusterization complete!"))

    @descr(_("Update clusterization (slow)"))
    def update_clusterization(self, request, queryset):
        self.force_clusterization(request, queryset, force=False)

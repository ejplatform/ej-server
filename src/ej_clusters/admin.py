from django.contrib import admin

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

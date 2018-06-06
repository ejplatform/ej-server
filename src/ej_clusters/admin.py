from django.contrib import admin

from . import models

admin.site.register(models.Stereotype)
admin.site.register(models.StereotypeVote)


class StereotypeClusterMapInline(admin.TabularInline):
    model = models.StereotypeClusterMap
    extra = 1


@admin.register(models.Cluster)
class ClusterAdmin(admin.ModelAdmin):
    inlines = [StereotypeClusterMapInline]

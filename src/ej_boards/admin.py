from django.contrib import admin

from . import models


class SubscriptionInline(admin.TabularInline):
    model = models.BoardSubscription
    fields = ['conversation']


@admin.register(models.Board)
class BoardAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'slug', 'members']
    list_display = ['title', 'owner', 'description', 'slug', 'members']
    list_filter = ['created']
    inlines = [SubscriptionInline]

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super().save_model(request, obj, form, change)

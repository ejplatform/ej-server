from django.contrib import admin

from . import models


@admin.register(models.Board)
class BoardAdmin(admin.ModelAdmin):
    fields = ['title', 'description', 'slug', 'conversations']
    list_display = ['title', 'owner', 'description', 'slug']
    list_filter = ['created']

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super().save_model(request, obj, form, change)

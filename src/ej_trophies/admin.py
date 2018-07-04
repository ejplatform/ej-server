from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from . import models

@admin.register(models.Trophy)
class TrophyAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Trophy definitions'), {'fields': [
            'key', 'name', 'short_description', 'full_description'
        ]}),
        (_('Icons'), {'fields': [
            'icon_not_started', 'icon_in_progress', 'icon_complete'
        ]}),
        (_('Gamification'), {'fields': [
            'score_percent', 'score_completed', 'completion_message'
        ]}),
        (_('Requirements'), {'fields': [
            'required_trophies', 'complete_on_required_satisfied'
        ]})
    )
    list_display = ('key', 'short_description')
    search_fields = ['key']

@admin.register(models.UserTrophy)
class UserTrophyAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Relationship'), {'fields': [
            'user', 'trophy'
        ]}),
        (_('Score'), {'fields': [
            'percentage'
        ]}),
        (_('Notification'), {'fields': [
            'notified'
        ]})
    )
    list_display = ('user', 'trophy', 'percentage', 'notified')
    search_fields = ['user', 'trophy']

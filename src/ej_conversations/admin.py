from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _
from . import models

SHOW_VOTES = getattr(settings, 'EJ_CONVERSATIONS_SHOW_VOTES', False)


class VoteInline(admin.TabularInline):
    model = models.Vote
    raw_id_fields = ['author']


class AuthorIsUserMixin(admin.ModelAdmin):
    author_field = 'author'

    def save_model(self, request, obj, *args, **kwargs):
        if getattr(obj, self.author_field) is None:
            setattr(obj, self.author_field, request.user)
        return super().save_model(request, obj, *args, **kwargs)


@admin.register(models.Comment)
class CommentAdmin(AuthorIsUserMixin, admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['conversation', 'content']}),
        (_('Moderation'), {'fields': ['status', 'rejection_reason']}),
    ]
    list_display = ['content', 'conversation', 'created', 'status']
    list_editable = ['status']
    list_filter = ['conversation', 'status', 'created']

    if SHOW_VOTES:
        inlines = [VoteInline]


@admin.register(models.Conversation)
class ConversationAdmin(AuthorIsUserMixin, admin.ModelAdmin):
    fields = ['title', 'text', 'is_promoted', 'is_hidden']
    list_display = ['title', 'slug', 'author', 'created', 'is_promoted', 'is_hidden']
    list_filter = ['created', 'is_promoted', 'is_hidden']
    list_editable = ['is_promoted', 'is_hidden']

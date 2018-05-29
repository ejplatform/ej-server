from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from .models import Conversation, Comment, Vote

register = (lambda model: lambda cfg: admin.site.register(model, cfg) or cfg)
SHOW_VOTES = getattr(settings, 'EJ_CONVERSATIONS_SHOW_VOTES', False)


class VoteInline(admin.TabularInline):
    model = Vote
    raw_id_fields = ['author']


class AuthorIsUserMixin(admin.ModelAdmin):
    def save_model(self, request, obj, *args, **kwargs):
        obj.author = request.user
        return super().save_model(request, obj, *args, **kwargs)


@register(Comment)
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


@register(Conversation)
class ConversationAdmin(AuthorIsUserMixin, admin.ModelAdmin):
    fields = ['title', 'question', 'status']
    list_display = ['title', 'slug', 'author', 'created']
    list_filter = ['status', 'created']

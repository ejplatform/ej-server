from django.conf import settings
from django.contrib import admin
from django.utils.translation import ugettext as _

from . import models

SHOW_VOTES = getattr(settings, 'EJ_CONVERSATIONS_SHOW_VOTES', False)
descr = (lambda msg: lambda f: setattr(f, 'short_description', msg) or f)


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
    fields = ['title', 'text', 'is_promoted', 'is_hidden', 'tags', 'limit_report_users']
    list_display = ['title', 'slug', 'author', 'created', 'is_promoted', 'is_hidden']
    list_filter = ['created', 'is_promoted', 'is_hidden']
    list_editable = ['is_promoted', 'is_hidden']
    actions = ['force_clusterization', 'update_clusterization']

    #
    # Clusterization actions
    #
    @descr(_('Force clusterization (slow)'))
    def force_clusterization(self, request, queryset, force=True):
        for conversation in queryset:
            clusterization = conversation.get_clusterization(None)
            clusterization.update_clusterization(force=force)
        self.message_user(request, _('Clusterization complete!'))

    @descr(_('Update clusterization (slow)'))
    def update_clusterization(self, request, queryset):
        self.force_clusterization(request, queryset, force=False)

    #
    # Gamification actions
    #
    @descr(_('Compute the opinion bridge user for all conversations.'))
    def compute_opinion_bridge(self, request, queryset):
        pass

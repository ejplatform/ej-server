from django.contrib import admin

from .models import Conversation, Comment, Vote


class CommentInline(admin.TabularInline):
    model = Comment


class VoteInline(admin.TabularInline):
    model = Vote


class ConversationAdmin(admin.ModelAdmin):
    fields = ['author', 'title', 'description', 'dialog', 'response', 'opinion', 'polis_id',
              'comment_nudge', 'comment_nudge_interval', 'comment_nudge_global_limit',
              'background_image', 'background_color', 'polis_url', 'polis_slug',
              'position', 'is_new']
    list_display = ['id', 'title', 'author', 'created_at', 'updated_at']


class CommentAdmin(admin.ModelAdmin):
    fields = ['conversation', 'author', 'content', 'polis_id', 'approval', 'rejection_reason']
    list_display = ['id', 'content', 'conversation', 'created_at', 'approval']
    list_editable = ['approval', ]
    list_filter = ['conversation', 'approval']
    inlines = [VoteInline]


admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Comment, CommentAdmin)

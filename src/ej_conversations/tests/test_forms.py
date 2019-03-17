from django.db import transaction

from ej_conversations.forms import CommentForm, ConversationForm
from ej_conversations.models import Comment


class TestConversationForm:
    def test_valid_conversation_form(self, db):
        form = ConversationForm({
            'title': 'conversation-slug',
            'tags': 'tag',
            'text': 'description',
            'comments_count': 1,
            'comment-1': 'comment',
        })
        assert form.is_valid()

    def test_conversation_form_save(self, db, user):
        form = ConversationForm({
            'title': 'conversation',
            'tags': 'tag',
            'text': 'description',
            'comments_count': 1,
            'comment-1': 'comment',
        })
        assert form.is_valid()
        with transaction.atomic():
            conversation = form.save_comments(author=user, is_promoted=True)

        assert conversation
        assert conversation.author == user
        assert conversation.title == 'conversation'
        assert conversation.tags.first().name == 'tag'
        assert conversation.comments.first().content == 'comment'
        assert conversation.comments.first().status == Comment.STATUS.approved

    def test_repeated_comments_error(self, conversation, db, user):
        Comment.objects.create(content="comment", conversation=conversation, author=user)
        form = CommentForm({'content': "comment"}, conversation=conversation)
        assert not form.is_valid()
        assert 'already submitted' in form.errors['content'][0]

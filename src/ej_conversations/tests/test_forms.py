import pytest
from django.db import transaction
from django.db.utils import IntegrityError

from ej_conversations.forms import CommentForm, ConversationForm
from ej_conversations.models import Comment
from ej_boards.models import Board


class TestConversationForm:
    def test_valid_form(self, db):
        form = ConversationForm({
            'title': 'conversation-slug',
            'tags': 'tag',
            'text': 'description',
            'comments_count': 0,
        })
        assert form.is_valid()

    def test_valid_form_with_comment(self, db):
        form = ConversationForm({
            'title': 'conversation-slug',
            'tags': 'tag',
            'text': 'description',
            'comments_count': 1,
            'comment-1': 'comment',
        })
        assert form.is_valid()

    def test_empty_form(self):
        form = ConversationForm({})
        assert not form.is_valid()
        assert form.errors == {
            'tags': ['This field is required.'],
            'title': ['This field is required.'],
            'text': ['This field is required.'],
            'comments_count': ['This field is required.'],
        }

    def test_conversation_form_save(self, db, user):
        title = 'conversation-slug1'
        form = ConversationForm({
            'title': title,
            'tags': 'tag',
            'text': 'description',
            'comments_count': 0,
        })
        form_is_valid = form.is_valid()
        assert form_is_valid
        with transaction.atomic():
            conversation = form.save_all(
                author=user,
                is_promoted=True,
            )
        assert conversation
        assert conversation.author == user
        assert conversation.title == title
        assert conversation.tags.first().name == 'tag'

    def test_conversation_form_save_with_comment(self, db, user):
        title = 'conversation-slug1'
        form = ConversationForm({
            'title': title,
            'tags': 'tag',
            'text': 'description',
            'comments_count': 1,
            'comment-1': 'comment',
        })
        form_is_valid = form.is_valid()
        assert form_is_valid
        with transaction.atomic():
            conversation = form.save_all(
                author=user,
                is_promoted=True,
            )
        assert conversation
        assert conversation.author == user
        assert conversation.title == title
        assert conversation.tags.first().name == 'tag'
        assert conversation.comments.first().content == 'comment'
        assert Comment.STATUS.approved == conversation.comments.first().status

    def test_conversation_form_save_with_board(self, db, user):
        title = 'conversation-slug1'
        form = ConversationForm({
            'title': title,
            'tags': 'tag',
            'text': 'description',
            'comments_count': 1,
        })
        board = Board.objects.create(owner=user, title='Title')
        form_is_valid = form.is_valid()
        assert form_is_valid
        with transaction.atomic():
            conversation = form.save_all(
                author=user,
                board=board,
            )
        assert conversation
        assert conversation.author == user
        assert conversation.title == title
        assert conversation.tags.first().name == 'tag'
        assert board.conversations.get(title=title) == conversation

    def test_conversation_form_save_without_comments(self, db, user):
        title = 'conversation-slug1'
        form = ConversationForm({
            'title': title,
            'tags': 'tag',
            'text': 'description',
            'comments_count': 1,
        })
        form_is_valid = form.is_valid()
        assert form_is_valid
        with transaction.atomic():
            conversation = form.save_all(
                author=user,
                is_promoted=True,
            )
        assert conversation
        assert conversation.author == user
        assert conversation.title == title
        assert conversation.tags.first().name == 'tag'
        assert conversation.comments.all().count() == 0

    def test_conversation_form_save_without_author(self, db):
        title = 'conversation-slug1'
        form = ConversationForm({
            'title': title,
            'tags': 'tag',
            'text': 'description',
            'comments_count': 1,
            'comment-1': 'comment',
        })
        form_is_valid = form.is_valid()
        assert form_is_valid
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                form.save_all(
                    author=None,
                    is_promoted=True,
                )


class TestCommentForm:
    def test_init(self, conversation):
        CommentForm(conversation=conversation)

    def test_init_without_conversation(self):
        with pytest.raises(TypeError):
            CommentForm()

    def test_valid_data(self, conversation, db, user):
        form = CommentForm({
            'content': "comment content",
        }, conversation=conversation)
        assert form.is_valid()
        comment = form.cleaned_data['content']
        conversation.create_comment(user, comment)
        assert comment == "comment content"

    def test_blank_data(self, conversation):
        form = CommentForm({}, conversation=conversation)
        assert not form.is_valid()
        assert form.errors == {
            'content': ['This field is required.'],
        }

    def test_repetead_comment_data(self, conversation, db, user):
        Comment.objects.create(content="Comment", conversation=conversation, author=user)
        form = CommentForm({
            'content': "Comment",
        }, conversation=conversation)
        assert not form.is_valid()
        print(form.errors['content'])
        assert form.errors['content'] == [
            'It seems that you created repeated comments. Please verify if there aren\'t any equal comments']

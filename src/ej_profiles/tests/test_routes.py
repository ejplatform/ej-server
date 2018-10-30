import pytest
from django.http import Http404

from ej.testing import UrlTester
from ej_profiles import routes
from ej_boards.models import Board
from ej_conversations.models import Conversation


class TestRoutes(UrlTester):
    user_urls = [
        '/profile/',
        '/profile/edit/',
        '/profile/conversations/'
    ]

    def test_comments_filter_bad_slug(self, rf, db, mk_user):
        request = rf.get('', {})
        request.user = mk_user
        with pytest.raises(Http404):
            routes.comments_tab(request, 'bad-slug')

    def test_comments_filter_approve(self, rf, db, mk_user):
        user = mk_user()
        request = rf.get('', {})
        request.user = user
        response = routes.comments_tab(request, 'approved')
        assert response['user'] == user
        assert not response['comments']
        assert not response['stats']

    def test_comments(self, rf, db, mk_user):
        user = mk_user()
        request = rf.get('', {})
        request.user = user
        response = routes.comments_list(request)
        assert response['user'] == user
        assert not response['comments']
        assert not response['stats']

    def test_profile_conversation_list(self, rf, db, user):
        user.save()
        conversation = Conversation.objects.create(author=user, title='title')
        conversation.save()
        request = rf.get('', {})
        request.user = user
        board = Board.objects.create(owner=user, title='titlea', slug='slugq')
        board.add_conversation(conversation)
        response = routes.conversations_list(request)
        assert response['user'].email == user.email
        assert response['conversations'][0].title == conversation.title
        assert response['current_board'].title == board.title
        assert response['create_url']
        assert response['boards']
        assert response['description']
        assert not response['can_add_conversation']

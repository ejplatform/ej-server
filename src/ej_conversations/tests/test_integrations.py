import pytest
import mock
from ej_conversations.models import Snapshot
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_boards.mommy_recipes import BoardRecipes


class TestSnapshotIntegrations(BoardRecipes):

    def test_generate_vote_url(self, mk_conversation, mk_board, mk_user):
        request = mock.Mock()
        request.META = {
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'ejplatform.local'
        }
        conversation = mk_conversation()
        user = mk_user(email="test@domain.com")
        comment_1 = conversation.create_comment(user, 'comment 1', 'approved')
        snapshot = Snapshot(conversation, request, 'mautic')
        expected_url = 'http://ejplatform.local/conversations/{}/{}?'\
            'comment_id={}&action=vote&origin=campaign'\
            .format(conversation.id, conversation.slug, comment_1.id)
        vote_url = snapshot.url_to_compute_vote()
        assert vote_url == expected_url

    def test_apply_default_palette_on_mail_template(self, mk_conversation, mk_board, mk_user):
        request = mock.Mock()
        request.META = {
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'ejplatform.local'
        }
        conversation = mk_conversation()
        user = mk_user(email="test2@domain.com")
        comment_1 = conversation.create_comment(user, 'comment 1', 'approved')
        arrow = 'border-top: 28px solid {} !important;'.format('#C4F2F4')
        dark = 'color: {} !important; background-color: {};'.format('#C4F2F4', '#30BFD3')
        light = 'color: {}; background-color: {};'.format('#30BFD3', '#C4F2F4')
        expected_palette = {
            'arrow': arrow,
            'dark': dark,
            'light': light,
            'light-h1': '',
            'dark-h1': ''
        }
        snapshot = Snapshot(conversation, request, 'mautic')
        palette = snapshot.get_conversation_palette()
        assert palette == expected_palette

    def test_generate_vote_url_with_board(self, mk_board, mk_conversation, mk_user):
        request = mock.Mock()
        request.META = {
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'ejplatform.local'
        }
        board = mk_board()
        user = mk_user(email="test@domain.com")
        conversation = mk_conversation(author=user)
        comment_1 = conversation.create_comment(user, 'comment 1', 'approved')
        board.add_conversation(conversation)
        snapshot = Snapshot(conversation, request, 'mautic')
        vote_url = snapshot.url_to_compute_vote()
        expected_url = 'http://ejplatform.local/{}/conversations/{}/{}?'\
            'comment_id={}&action=vote&origin=campaign'.format(board.slug,
                                                               conversation.id,
                                                               conversation.slug,
                                                               comment_1.id)
        assert vote_url == expected_url

    def test_apply_board_palette_on_campaign_template(self, mk_board, mk_conversation, mk_user):
        request = mock.Mock()
        request.META = {
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'ejplatform.local'
        }
        board = mk_board(palette='orange')
        user = mk_user(email="test@domain.com")
        conversation = mk_conversation(author=user)
        comment_1 = conversation.create_comment(user, 'comment 1', 'approved')
        board.add_conversation(conversation)
        snapshot = Snapshot(conversation, request, 'mautic')
        arrow = 'border-top: 28px solid {} !important;'.format('#FFE1CA')
        dark = 'color: {} !important; background-color: {};'.format('#FFE1CA', '#F5700A')
        light = 'color: {}; background-color: {};'.format('#F5700A', '#FFE1CA')
        expected_palette = {
            'arrow': arrow,
            'dark': dark,
            'light': light,
            'light-h1': '',
            'dark-h1': ''
        }
        host_url = 'http://ejplatform.local'
        snapshot = Snapshot(conversation, request, 'mautic')
        palette = snapshot.get_conversation_palette()
        assert palette == expected_palette

    def test_apply_campaign_palette_on_mail_template(self, mk_board, mk_conversation, mk_user):
        request = mock.Mock()
        request.META = {
            'wsgi.url_scheme': 'http',
            'HTTP_HOST': 'ejplatform.local'
        }
        board = mk_board(palette='campaign')
        user = mk_user(email="test@domain.com")
        conversation = mk_conversation(author=user)
        comment_1 = conversation.create_comment(user, 'comment 1', 'approved')
        board.add_conversation(conversation)
        snapshot = Snapshot(conversation, request, 'mautic')
        arrow = 'border-top: 28px solid {} !important;'.format('#332f82')
        dark = 'color: {} !important; background-color: {}; border-radius: unset;'.format('#332f82', '#1c9dd9')
        light = 'color: {}; background-color: {}; border-radius: unset;'.format('#1c9dd9', '#332f82')
        expected_palette = {
            'arrow': arrow,
            'dark': dark,
            'light': light,
            'light-h1': 'color: #ffffff !important;',
            'dark-h1': 'color: #1c9dd9 !important;'
        }
        host_url = 'http://ejplatform.local'
        campaign = Snapshot(conversation, request, 'mautic')
        palette = snapshot.get_conversation_palette()
        assert palette == expected_palette

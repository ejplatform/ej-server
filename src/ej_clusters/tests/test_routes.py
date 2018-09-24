import pytest
from django.test import Client
from django.test import TestCase

from ej.testing import UrlTester
from ej_conversations.mommy_recipes import ConversationRecipes
from ej_users.models import User
from ej_conversations.models import Conversation, Choice
from ej_clusters.models import Stereotype, StereotypeVote
from ej_clusters.mommy_recipes import ClustersRecipes


class TestRoutes(UrlTester, ConversationRecipes, ClustersRecipes):
    owner_urls = [
        '/conversations/conversation/stereotypes/add/',
        '/conversations/conversation/stereotypes/',
        # '/conversations/conversation/stereotypes/1/edit'
    ]

    @pytest.fixture
    def data(self, conversation, author_db, stereotype):
        conversation.author = author_db
        conversation.save()
        stereotype.owner = author_db
        stereotype.conversation = conversation
        stereotype.save()
        return {
            'conversation': conversation.__dict__,
            'author': author_db.__dict__,
            'stereotype': stereotype.__dict__,
        }


class TestStereotypeRoutes(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('name@server.com', '1234', name='name')
        self.conversation = Conversation.objects.create(title='Title', author=self.user)
        comment = self.conversation.create_comment(self.user, 'comment', 'approved')
        client = Client()
        client.force_login(self.user)
        self.logged_client = client
        self.stereotype = Stereotype.objects.create(name='stereo', conversation=self.conversation, owner=self.user)
        StereotypeVote.objects.create(author=self.stereotype, choice=Choice.SKIP, comment=comment)

    def test_create_stereotype(self):
        client = self.logged_client
        response = client.post(self.conversation.get_absolute_url() + 'stereotypes/add/',
                               data={'name': 'something',
                                     'form-TOTAL_FORMS': 1,
                                     'form-INITIAL_FORMS': 0,
                                     'form-MIN_NUM_FORMS': 0,
                                     'form-MAX_NUM_FORMS': 1000,
                                     'form-0-comment': '1',
                                     'form-0-choice': '0',
                                     'form-0-id': ''})
        print(response.content)
        self.assertRedirects(response, self.conversation.get_absolute_url() + 'stereotypes/', 302, 200)

    def test_create_invalid_stereotype(self):
        client = self.logged_client
        response = client.post(self.conversation.get_absolute_url() + 'stereotypes/add/',
                               data={'name': '',
                                     'form-TOTAL_FORMS': 1,
                                     'form-INITIAL_FORMS': 0,
                                     'form-MIN_NUM_FORMS': 0,
                                     'form-MAX_NUM_FORMS': 1000,
                                     'form-0-comment': '',
                                     'form-0-choice': 0,
                                     'form-0-id': ''})
        self.assertEqual(response.status_code, 200)

    def test_edit_stereotype(self):
        client = self.logged_client
        response = client.post(self.conversation.get_absolute_url() +
                               'stereotypes/' + str(self.stereotype.id) + '/edit/',
                               data={'name': 'stereo',
                                     'form-TOTAL_FORMS': 1,
                                     'form-INITIAL_FORMS': 0,
                                     'form-MIN_NUM_FORMS': 0,
                                     'form-MAX_NUM_FORMS': 1000,
                                     'form-0-comment': '1',
                                     'form-0-choice': '1',
                                     'form-0-id': ''})
        print(response.content)
        self.assertRedirects(response, self.conversation.get_absolute_url() + 'stereotypes/', 302, 200)

    def test_edit_invalid_stereotype(self):
        client = self.logged_client
        response = client.post(self.conversation.get_absolute_url() +
                               'stereotypes/' + str(self.stereotype.id) + '/edit/',
                               data={'name': '',
                                     'form-TOTAL_FORMS': 1,
                                     'form-INITIAL_FORMS': 0,
                                     'form-MIN_NUM_FORMS': 0,
                                     'form-MAX_NUM_FORMS': 1000,
                                     'form-0-comment': '1',
                                     'form-0-choice': 1,
                                     'form-0-id': ''})
        self.assertEqual(response.status_code, 200)

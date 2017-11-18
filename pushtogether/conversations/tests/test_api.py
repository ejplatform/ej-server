import json
import pytest
from pprint import pprint

from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from pushtogether.conversations.serializers import (
    AuthorSerializer,
    ConversationSerializer,
    CommentSerializer,
    VoteSerializer,
)
from pushtogether.conversations.models import (
    Conversation,
    Comment,
    Vote,
)

from .helpers import TestBase

pytestmark = pytest.mark.django_db

class TestConversationAPI(TestBase):

    def setup(self):
        super(TestConversationAPI, self).setup()
        self.create_read_url = reverse(
            "{version}:{name}".format(
                version='v1',
                name='conversation-list'
            )
        )

    def test_get_list_without_login_should_return_401(self, client):
        response = client.get(self.create_read_url)
        assert response.status_code == 200

    def test_get_list_logged_in_should_return_200(self, client):
        client.force_login(self.user)
        response = client.get(self.create_read_url)
        assert response.status_code == 200

    def test_get_list_should_contains_this_conversation(self, client):
        client.force_login(self.user)
        response = client.get(self.create_read_url)

        assert 'test_title' in str(response.content)

    def test_create_conversation(self, client):
        """
        Ensure we can create a new conversation object.
        """
        client.force_login(self.user)
        last_conversation_count = Conversation.objects.count()
        user_serializer = AuthorSerializer(self.user)
        author_json_data = user_serializer.data

        data = {
            "author": self.user.id,
            "description": "test_description",
            "title": "test_title",
            "created_at": str(timezone.now()),
            "updated_at": str(timezone.now()),
        }

        pprint(data)

        response = client.post(self.create_read_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Conversation.objects.count() > last_conversation_count
        assert Conversation.objects.last().title == 'test_title'

    def test_update_conversation(self, client):
        """
        Ensure we can update a conversation object.
        """
        client.force_login(self.user)

        update_url = reverse("%s:%s" % ('v1', 'conversation-detail'),
                             args=(self.conversation.id,))

        data = json.dumps({
            "title": "new_test_title",
            "description": "new_test_description",
        })

        pre_update_response = client.get(self.create_read_url)
        update_response = client.patch(
            update_url, data,
            content_type='application/json'
        )
        post_update_response = client.get(self.create_read_url)


        assert pre_update_response.status_code == status.HTTP_200_OK
        assert update_response.status_code == status.HTTP_200_OK
        assert post_update_response.status_code == status.HTTP_200_OK
        assert 'test_title' == pre_update_response.data[0]['title']
        assert 'new_test_title' == post_update_response.data[0]['title']
        assert Conversation.objects.last().title == 'new_test_title'

    def test_delete_conversations(self, client):
        """
        Ensure we can delete a conversation object.
        """
        client.force_login(self.user)
        last_conversation_counter = Conversation.objects.count()
        delete_url = reverse("%s:%s" % ('v1', 'conversation-detail'),
                             args=(self.conversation.id,))

        response = client.delete(delete_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Conversation.objects.count() < last_conversation_counter

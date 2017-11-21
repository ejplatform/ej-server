import json
import pytest
import time
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
        self.update_url = reverse(
            "{version}:{name}".format(
                version='v1',
                name='conversation-detail'),
            args=(self.conversation.id,)
        )
        self.delete_url = reverse(
            "{version}:{name}".format(
                version='v1',
                name='conversation-detail'),
            args=(self.conversation.id,)
        )

    def teardown(self):
        self.conversation.comments.all().delete()

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

        data = json.dumps({
            "title": "new_test_title",
            "description": "new_test_description",
        })

        update_response = client.patch(
            self.update_url, data,
            content_type='application/json'
        )
        post_update_response = client.get(self.create_read_url)


        assert update_response.status_code == status.HTTP_200_OK
        assert 'new_test_title' in str(post_update_response.content)

    def test_delete_conversations(self, client):
        """
        Ensure we can delete a conversation object.
        """
        client.force_login(self.user)
        last_conversation_counter = Conversation.objects.count()

        response = client.delete(self.delete_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Conversation.objects.count() < last_conversation_counter

    # [TODO] should be a helper function
    def post_valid_comment(self, client, conversation, number=1):
        data = json.dumps({
            "conversation": conversation.id,
            "content": "test_content",
        })
        create_comment_url = reverse(
            "{version}:{name}".format(
                version='v1',
                name='comment-list')
        )
        for i in range(number):
            response = client.post(
                create_comment_url, data, content_type='application/json')
        return response

    def test_nudge_is_user_eager_with_multiple_comments(self, client):
        '''
        Should return true if user is trying to post too much comments
        '''
        client.force_login(self.user)
        self.conversation.comment_nudge = 6
        self.conversation.comment_nudge_interval = 10
        self.conversation.save()

        response = self.post_valid_comment(client, self.conversation, number=4)

        assert response.data['nudge'] == Conversation.NUDGE.eager.value

    def test_nudge_is_user_eager_respecting_time_limit(self, client):
        '''
        Should return not an eager if user respect the time limit
        '''
        client.force_login(self.user)
        self.conversation.comment_nudge = 4
        self.conversation.comment_nudge_interval = 2
        self.conversation.save()

        response = self.post_valid_comment(client, self.conversation)

        assert response.data['nudge'] != Conversation.NUDGE.eager.value

    def test_nudge_is_user_eager_distributing_comments_in_the_time(self, client):
        '''
        Should return not an eager if user respect the total time limit
        '''
        client.force_login(self.user)
        self.conversation.comment_nudge = 4
        self.conversation.comment_nudge_interval = 1
        self.conversation.save()

        self.post_valid_comment(client, self.conversation)
        time.sleep(2)
        response = self.post_valid_comment(client, self.conversation)

        assert response.data['nudge'] != Conversation.NUDGE.eager

    def test_nudge_is_user_interval_blocked(self, client):
        '''
        Should return interval blocked if user post too many comments,
        disrespecting time limits
        '''
        client.force_login(self.user)
        self.conversation.comment_nudge = 1
        self.conversation.comment_nudge_interval = 10
        self.conversation.save()

        response = self.post_valid_comment(client, self.conversation, number=2)

        assert response.data['nudge'] == Conversation.NUDGE.interval_blocked.value

    def test_nudge_is_user_global_limit_blocked(self, client):
        '''
        Should not return global_blocked if user post many comments disrespecting
        the nudge global limits
        '''
        client.force_login(self.user)
        self.conversation.comment_nudge_global_limit = 1
        self.conversation.save()

        response = self.post_valid_comment(client, self.conversation)

        assert response.data['nudge'] == Conversation.NUDGE.normal.value


    def test_nudge_status_should_return_normal(self, client):
        '''
        Should return normal if user is respecting nudge limits and post
        moderately
        '''
        client.force_login(self.user)
        self.conversation.comment_nudge_global_limit = 5
        self.conversation.comment_nudge = 4
        self.conversation.comment_nudge_interval = 4
        self.conversation.save()

        response = self.post_valid_comment(client, self.conversation)

        assert response.data['nudge'] == Conversation.NUDGE.normal.value

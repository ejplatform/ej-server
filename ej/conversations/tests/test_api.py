import json
import time

import pytest
from django.utils import timezone
from rest_framework import status

from ej.conversations.models import (
    Conversation,
)
from .helpers import post_valid_comment

pytestmark = pytest.mark.django_db


class TestConversationAPI:

    def update_url(self, conversation):
        return f'/api/conversations/{conversation.id}/'

    def delete_url(self, conversation):
        return f'/api/conversations/{conversation.id}/'

    def create_read_url(self):
        return '/api/conversations/'

    def test_get_list_without_login_should_return_200(self, client):
        response = client.get(self.create_read_url())
        assert response.status_code == status.HTTP_200_OK

    def test_get_list_logged_in_should_return_200(self, client, user):
        client.force_login(user)
        response = client.get(self.create_read_url())
        assert response.status_code == status.HTTP_200_OK

    def test_get_list_should_contains_this_conversation(self, client, user, conversation):
        client.force_login(user)
        response = client.get(self.create_read_url())

        assert conversation.title in str(response.content)

    def test_create_conversation(self, client, user):
        """
        Ensure we can't create a new conversation object.
        """
        client.force_login(user)
        last_conversation_count = Conversation.objects.count()
        data = {
            "author": user.id,
            "description": "test_description",
            "title": "test_title",
            "created_at": str(timezone.now()),
            "updated_at": str(timezone.now()),
        }

        response = client.post(self.create_read_url(), data, format='json')

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert Conversation.objects.count() == last_conversation_count

    def test_user_cant_update_conversation(self, client, user, conversation):
        """
        Ensure we can't update a conversation object.
        """
        client.force_login(user)
        data = json.dumps({
            "title": "new_test_title",
            "description": "new_test_description",
        })
        update_response = client.patch(
            self.update_url(conversation), data,
            content_type='application/json'
        )

        assert update_response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_user_cant_delete_conversations(self, client, user, conversation):
        """
        Ensure we can't delete a conversation object.
        """
        client.force_login(user)
        last_conversation_counter = Conversation.objects.count()

        response = client.delete(self.delete_url(conversation))

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert Conversation.objects.count() == last_conversation_counter

    def test_nudge_is_user_eager_with_multiple_comments(self, client, user, conversation):
        """
        Should return true if user is trying to post too much comments
        """
        client.force_login(user)
        conversation.comment_nudge = 6
        conversation.comment_nudge_interval = 10
        conversation.save()

        response = post_valid_comment(client, conversation, number=5)

        assert response.data['nudge'] == Conversation.NUDGE.eager.value

    def test_nudge_is_user_eager_respecting_time_limit(self, client, user, conversation):
        """
        Should return not an eager if user respect the time limit
        """
        client.force_login(user)
        conversation.comment_nudge = 4
        conversation.comment_nudge_interval = 2
        conversation.save()

        response = post_valid_comment(client, conversation)

        assert response.data['nudge'] != Conversation.NUDGE.eager.value

    def test_nudge_is_user_eager_distributing_comments_in_the_time(self, client, user, conversation):
        """
        Should return not an eager if user respect the total time limit
        """
        client.force_login(user)
        conversation.comment_nudge = 4
        conversation.comment_nudge_interval = 1
        conversation.save()

        post_valid_comment(client, conversation)
        time.sleep(2)
        response = post_valid_comment(client, conversation)

        assert response.data['nudge'] != Conversation.NUDGE.eager

    def test_nudge_is_user_interval_blocked(self, client, user, conversation):
        """
        Should return interval blocked if user post too many comments,
        disrespecting time limits
        """
        client.force_login(user)
        conversation.comment_nudge = 1
        conversation.comment_nudge_interval = 10
        conversation.save()

        response = post_valid_comment(client, conversation, number=2)

        assert response.data['nudge'] == Conversation.NUDGE.interval_blocked.value

    def test_nudge_is_user_global_limit_blocked(self, client, user, conversation):
        """
        Should not return global_blocked if user post many comments disrespecting
        the nudge global limits
        """
        client.force_login(user)
        conversation.comment_nudge_global_limit = 1
        conversation.save()

        response = post_valid_comment(client, conversation)

        assert response.data['nudge'] == Conversation.NUDGE.global_blocked.value
        assert response.status_code == status.HTTP_201_CREATED

    def test_nudge_status_should_return_normal(self, client, user, conversation):
        """
        Should return normal if user is respecting nudge limits and post
        moderately
        """
        client.force_login(user)
        conversation.comment_nudge_global_limit = 5
        conversation.comment_nudge = 4
        conversation.comment_nudge_interval = 4
        conversation.save()

        response = post_valid_comment(client, conversation)

        assert response.data['nudge'] == Conversation.NUDGE.normal.value

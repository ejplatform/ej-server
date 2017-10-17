import json

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from pushtogether.conversations.models import (
    Conversation,
    Comment,
    Vote,
)


class DjangoRestFrameworkTests(APITestCase):

    def setUp(self):
        user = get_user_model().objects.create(
            username = "test_user",
            password = "test_password",
        )
        user.save()

        conversation = Conversation.objects.create(
            author = user,
            title = "test_title",
            description = "test_description",
        )
        conversation.save()

        comment = Comment.objects.create(
            author = user,
            conversation = conversation,
            content = "test_content",
            polis_id = '1234',
            approval = Comment.APPROVED
        )
        comment.save()

        vote = Vote.objects.create(
            author = user,
            comment = comment,
            polis_id = '12345',
            value = Vote.AGREE
        )
        vote.save()

        self.user = user
        self.create_read_url = reverse('conversation-list')

    def test_get_list_without_login_should_return_403(self):
        response = self.client.get(self.create_read_url)
        assert response.status_code == 403

    def test_get_list_logged_in_should_return_200(self):
        self.client.force_login(self.user)
        response = self.client.get(self.create_read_url)
        assert response.status_code == 200

    def test_get_list_should_contains_this_conversation(self):
        self.client.force_login(self.user)
        response = self.client.get(self.create_read_url)

        #Is the title in the content
        self.assertContains(response, 'test_title')

    def test_create_conversation(self):
        self.client.force_authenticate(self.user)
        last_conversation_counter = Conversation.objects.count()
        
        data = {
            'title': 'test_title',
            'description': 'test_description',
        }

        response = self.client.post(self.create_read_url, data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert Conversation.objects.count() > last_conversation_counter
        assert Conversation.objects.last().name == 'test_title'

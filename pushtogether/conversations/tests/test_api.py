import json

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from pushtogether.conversations.models import (
    Conversation,
    Comment,
    Vote,
)


class DjangoRestFrameworkTests(TestCase):

    def setUp(self):
        user = get_user_model().objects.create(
            username = "test_user",
        )

        conversation = Conversation.objects.create(
            author = user,
            title = "test_title",
            description = "test_description",
        )

        comment = Comment.objects.create(
            author = user,
            conversation = conversation,
            content = "test_content",
            polis_id = '1234',
            approval = Comment.APPROVED
        )

        vote = Vote.objects.create(
            author = user,
            comment = comment,
            polis_id = '12345',
            value = Vote.AGREE
        )

        self.user = user
        self.create_read_url = reverse('conversation-list')

    def test_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.create_read_url)

        #Is the title in the content
        self.assertContains(response, 'test_title')


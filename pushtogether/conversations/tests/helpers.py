import pytest
import json

from django.contrib.auth import get_user_model
from django.urls import reverse

from pushtogether.conversations.models import (
    Conversation,
    Comment,
    Vote,
)


pytestmark = pytest.mark.django_db


def create_valid_user(username):
    user = get_user_model().objects.create(
        username=username,
        password="test_password",
        first_name="test",
        last_name="user",
        is_superuser=True,
    )
    user.set_password("test_password")
    user.save()
    return user


def create_valid_conversation(user):
    conversation = Conversation.objects.create(
        author=user,
        title="test_title",
        description="test_description",
    )
    conversation.save()
    return conversation


def create_valid_comment(conversation, user, approval=Comment.APPROVED):
    comment = Comment.objects.create(
        author=user,
        conversation=conversation,
        content="test_content",
        polis_id='1234',
        approval=approval
    )
    comment.save()
    return comment


def create_valid_comments(number, conversation, user, approval=Comment.APPROVED):
    return [create_valid_comment(conversation, user, approval)
            for x in range(number)]


def create_valid_vote(comment, user, value=Vote.AGREE):
    vote = Vote.objects.create(
        author=user,
        comment=comment,
        polis_id='12345',
        value=Vote.AGREE
    )
    vote.save()
    return vote


def post_valid_comment(client, conversation, number=1):
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

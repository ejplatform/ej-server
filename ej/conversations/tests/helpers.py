import pytest
import json
import random

from django.contrib.auth import get_user_model
from django.urls import reverse

from ej.conversations.models import (
    Conversation,
    Comment,
    Vote,
)


pytestmark = pytest.mark.django_db


def create_valid_user(username, is_superuser=True):
    user = get_user_model().objects.create(
        username=username,
        password="test_password",
        first_name="test",
        last_name="user",
        is_superuser=is_superuser,
    )
    user.set_password("test_password")
    user.save()
    return user


def create_valid_users(number):
    return [create_valid_user("test_user_" + str(x), is_superuser=False)
            for x in range(number)]


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
        value=Vote.AGREE
    )
    vote.save()
    return vote


def populate_conversation_comments(conversation, users_list, n_comments_per_user=1):
    for user in users_list:
        create_valid_comments(n_comments_per_user, conversation, user)
    return conversation.comments


def populate_conversation_votes(conversation, users_list, max_votes_per_user):
    possible_votes = [Vote.AGREE, Vote.DISAGREE]
    comments_count = conversation.comments.count()
    if max_votes_per_user > comments_count:
        max_votes_per_user = comments_count

    list_of_comments = list(conversation.comments.all())
    for user in users_list:
        for comment in random.sample(list_of_comments, max_votes_per_user):
            if comment.author != user:
                create_valid_vote(comment, user, value=random.choice(possible_votes))


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

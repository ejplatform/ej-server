from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import routers, serializers, viewsets
from .models import Conversation, Comment, Vote


User = get_user_model()

class AuthorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'url', 'name')


class ConversationSerializer(serializers.HyperlinkedModelSerializer):
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'url', 'author', 'title','description')


class CommentSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('conversation', 'author','content')


class VoteSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    comment = CommentSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ('conversation', 'author','comment', 'value')

from django.conf.urls import url, include
from .models import Conversation, Comment, Vote
from rest_framework import routers, serializers, viewsets
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()

class AuthorSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name')


class ConversationSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    participants = AuthorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('author', 'participants', 'title','description')


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

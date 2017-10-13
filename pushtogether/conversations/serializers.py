from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import routers, serializers, viewsets
from .models import Conversation, Comment, Vote


User = get_user_model()

class AuthorSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'url', 'username')


class ConversationSerializer(serializers.HyperlinkedModelSerializer):
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'url', 'author', 'title','description')


class CommentReportSerializer(serializers.ModelSerializer):
    total_votes = serializers.SerializerMethodField()
    agree_votes = serializers.SerializerMethodField()
    disagree_votes = serializers.SerializerMethodField()
    pass_votes = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('id', 'total_votes', 'agree_votes',
            'disagree_votes', 'pass_votes')

    def get_agree_votes(self, obj):
        return Vote.objects.filter(comment_id=obj.id, value=Vote.AGREE).count()

    def get_disagree_votes(self, obj):
        return Vote.objects.filter(comment_id=obj.id, value=Vote.DISAGREE).count()

    def get_pass_votes(self, obj):
        return Vote.objects.filter(comment_id=obj.id, value=Vote.PASS).count()

    def get_total_votes(self, obj):
        return obj.votes.count()


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    comment_report = CommentReportSerializer(read_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'url', 'conversation', 'author', 'content', 'approval',
            'comment_report')


class VoteSerializer(serializers.ModelSerializer):
    conversation = ConversationSerializer(read_only=True)
    author = AuthorSerializer(read_only=True)
    comment = CommentSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ('conversation', 'author','comment', 'value')

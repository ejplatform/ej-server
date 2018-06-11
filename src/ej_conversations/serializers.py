from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers

from ej_conversations.models import VOTE_NAMES
from .mixins import HasAuthorSerializer, HasLinksSerializer, join_url
from .models import Conversation, Comment, Vote


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('url', 'username')
        extra_kwargs = {'url': {'lookup_field': 'username'}}


class ConversationSerializer(HasAuthorSerializer):
    statistics = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('links', 'title', 'question', 'slug', 'author_name',
                  'created', 'modified', 'is_promoted', 'statistics')
        extra_kwargs = {
            'url': {'lookup_field': 'slug'},
        }

    def get_inner_links(self, obj):
        return ['user_data', 'votes', 'approved_comments', 'random_comment']

    def get_links(self, obj):
        links = super().get_links(obj)
        path = reverse('category-detail', kwargs={'slug': obj.category.slug})
        links['category'] = join_url(self.url_prefix, path)
        return links

    def get_statistics(self, obj):
        try:
            return obj._statistics
        except AttributeError:
            obj._statistics = statistics = obj.statistics()
            return statistics

    def get_category_name(self, obj):
        return obj.category.name


class CommentSerializer(HasAuthorSerializer):
    statistics = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ('links', 'id', 'content', 'author_name',
                  'status', 'created', 'modified', 'rejection_reason',
                  'conversation', 'statistics')
        read_only_fields = ('id', 'author', 'status', 'rejection_reason')
        extra_kwargs = {
            'category': {'lookup_field': 'slug'},
            'conversation': {'write_only': True, 'lookup_field': 'slug'},
        }

    def get_inner_links(self, obj):
        return ['vote']

    def get_links(self, obj):
        payload = super().get_links(obj)
        payload['conversation'] = self.url_prefix + reverse(
            'conversation-detail', kwargs={'slug': obj.conversation.slug}
        )
        return payload

    def create(self, validated_data):
        conversation = validated_data.pop('conversation')
        return conversation.create_comment(**validated_data)

    def get_statistics(self, obj):
        return obj.statistics()


class VoteSerializer(HasLinksSerializer):
    comment_text = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()

    class Meta:
        model = Vote
        fields = ('links', 'comment_text', 'action', 'comment', 'value')
        extra_kwargs = {
            'comment': {'write_only': True},
            'value': {'write_only': True},
        }

    def get_links(self, obj):
        payload = super().get_links(obj)
        path = reverse('comment-detail', kwargs={'pk': obj.comment.pk})
        payload['comment'] = self.url_prefix + path
        return payload

    def get_comment_text(self, obj):
        return obj.comment.content

    def get_action(self, obj):
        return VOTE_NAMES[obj.value]

    def create(self, data):
        comment = data.pop('comment')
        return comment.vote(**data)

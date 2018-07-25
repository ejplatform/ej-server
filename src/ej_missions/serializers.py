from rest_framework import serializers
import datetime

from . import models
from ej_conversations.models import Comment as ConversationComment
from .mixins import MissionMixin
from ej_trophies.models.user_trophy import UserTrophy
from ej_users.models import User


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'id', 'email', 'name')

class CommentSerializer(serializers.ModelSerializer):
    user = OwnerSerializer(read_only=True)

    class Meta:
        model = models.Comment
        fields = ('user', 'comment')

class ConversationCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationComment
        fields = '__all__'

class MissionSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    comment_set = CommentSerializer(many=True)
    remainig_days = serializers.SerializerMethodField()
    pending_conversations = serializers.SerializerMethodField()

    def get_remainig_days(self, obj):
        deadline_in_days = (obj.deadline - datetime.date.today()).days

        if(deadline_in_days < 0):
            return "missão encerrada"
        if(deadline_in_days == 0):
            return "encerra hoje"
        if(deadline_in_days == 1):
            return "encerra amanhã"

        return "{} dias restantes".format(deadline_in_days);

    def get_pending_conversations(self, obj):
        pending_conversations = obj.conversations.filter(comments__votes=None)
        return list(set(map(lambda x: x.id, pending_conversations)))

    class Meta:
        model = models.Mission
        fields = ('id', 'title', 'description', 'users', 'image',
                  'youtubeVideo', 'audio', 'owner', 'remainig_days',
                  'deadline', 'comment_set',
                  'reward', 'pending_conversations', 'conversations')

class MissionInboxSerializer(MissionMixin, MissionSerializer):

    blocked = serializers.SerializerMethodField()

    class Meta:
        model = models.Mission
        fields='__all__'

class MissionReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Receipt
        fields = ('id',
                  'userName',
                  'userEmail',
                  'status',
                  'description',
                  'receiptFile',
                  'user')


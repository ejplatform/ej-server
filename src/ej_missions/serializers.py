from . import models
from ej_users.models import User
from rest_framework import serializers
from ej_trophies.models.user_trophy import UserTrophy
from .mixins import MissionMixin
import datetime


class OwnerSerializer(serializers.ModelSerializer):
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('display_name', 'id', 'email', 'name', 'profile_id')

    def get_profile_id(self, obj):
        return obj.profile.id

class CommentSerializer(serializers.ModelSerializer):
    user = OwnerSerializer(read_only=True)

    class Meta:
        model = models.Comment
        fields = ('user', 'comment')

class MissionSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    comment_set = CommentSerializer(many=True)
    remainig_days = serializers.SerializerMethodField()

    def get_remainig_days(self, obj):
        deadline_in_days = (obj.deadline - datetime.date.today()).days

        if(deadline_in_days < 0):
            return "missão encerrada"
        if(deadline_in_days == 0):
            return "encerra hoje"
        if(deadline_in_days == 1):
            return "encerra amanhã"

        return "{} dias restantes".format(deadline_in_days);

    class Meta:
        model = models.Mission
        fields = ('id', 'title', 'description', 'users', 'image',
                  'youtubeVideo', 'audio', 'owner', 'remainig_days',
                  'deadline', 'comment_set', 'reward')

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


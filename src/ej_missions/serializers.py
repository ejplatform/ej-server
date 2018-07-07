from . import models
from ej_users.models import User
from rest_framework import serializers


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'id', 'email', 'name')

class CommentSerializer(serializers.ModelSerializer):
    user = OwnerSerializer(read_only=True)

    class Meta:
        model = models.Comment
        fields = ('user', 'comment')

class MissionSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)
    comment_set = CommentSerializer(many=True)

    class Meta:
        model = models.Mission
        fields = ('id', 'title', 'description', 'users', 'image', 'youtubeVideo', 'audio', 'owner', 'remainig_days', 'deadline', 'comment_set', 'reward')

class MissionInboxSerializer(MissionSerializer):
    blocked = serializers.BooleanField()
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


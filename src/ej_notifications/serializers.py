from . import models
from ej_users.models import User
from ej_channels.models import Channel
from ej_messages.models import Message
from rest_framework import serializers
import datetime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'id', 'email', 'name')

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('name' ,'id', 'sort')

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('title', 'body', 'link', 'target')

class NotificationSerializer(serializers.ModelSerializer):
    receiver = UserSerializer(read_only=True)
    channel = ChannelSerializer(read_only=True)
    message = MessageSerializer(read_only=True)

    class Meta:
        model = models.Notification
        fields = ('id', 'receiver', 'read', 'created_at', 'channel', 'message')


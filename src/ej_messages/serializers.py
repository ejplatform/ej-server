from . import models
from ej_users.models import User
from ej_channels.models import Channel
from rest_framework import serializers
import datetime

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('name' ,'id', 'sort')

class MessageSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer(read_only=True)

    class Meta:
        model = models.Message
        fields = ('id', 'title', 'body', 'channel', 'created_at')
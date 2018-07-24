from . import models
from ej_users.models import User
from rest_framework import serializers
import datetime

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Channel
        fields = ('id', 'name', 'users', 'created_at')
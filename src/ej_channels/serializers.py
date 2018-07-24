from . import models
from ej_users.models import User
from rest_framework import serializers
import datetime

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'id', 'email', 'name')
        
class ChannelSerializer(serializers.ModelSerializer):
    users = UsersSerializer(read_only=True, many=True)

    class Meta:
        model = models.Channel
        fields = ('id', 'name', 'users', 'created_at','sort')
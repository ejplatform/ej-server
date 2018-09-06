from . import models
from ej_users.models import User
from rest_framework import serializers


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'id', 'email', 'name')


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name')


class ChannelSerializer(serializers.ModelSerializer):
    users = UsersSerializer(read_only=True, many=True)
    owner = OwnerSerializer(read_only=True)

    class Meta:
        model = models.Channel
        fields = ('id', 'name', 'users', 'created_at', 'sort', 'owner')

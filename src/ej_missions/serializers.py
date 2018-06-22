from . import models
from ej_users.models import User
from rest_framework import serializers


class MissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mission
        fields = ('id', 'title', 'description', 'users')

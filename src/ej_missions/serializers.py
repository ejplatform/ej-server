from . import models
from ej_users.models import User
from rest_framework import serializers


class MissionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Mission
        fields = ('title', 'description', 'users')

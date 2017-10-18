from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import routers, serializers, viewsets
from .models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'url', 'name', 'email', 'city', 'state', 'country',
                  'race', 'gender', 'occupation', 'age', 'political_movement')

from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import routers, serializers, viewsets
from .models import User


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'image', 'name', 'email', 'biography', 'city',
                  'state', 'country', 'username', 'race', 'gender',
                  'occupation', 'age', 'political_movement')

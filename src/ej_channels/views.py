from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.request import Request
import json
from django import forms
from django.http import QueryDict

from . import serializers
from . import models
from ej_users.models import User

class ChannelViewSet(viewsets.ViewSet):

    def index(self, request):
        queryset = models.Channel.objects.all().order_by("-created_at")
        serializer = serializers.ChannelSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        channel = models.Channel(name=data["name"])

        channel.save()
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)
        
    def add_to_channel(self, request):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.filter(id=data["id"])[0]
        channel.users.add(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)

    def remove_from_channel(self, request):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.filter(id=data["id"])[0]
        channel.users.remove(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)

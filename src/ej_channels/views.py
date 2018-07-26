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
        queryset = models.Channel.objects.all().order_by("id")
        serializer = serializers.ChannelSerializer(queryset, many=True)
        return Response(serializer.data)

    def show(self, request, pk):
        queryset = models.Channel.objects.get(id=pk)
        serializer = serializers.ChannelSerializer(queryset)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        channel = models.Channel(name=data["name"], owner=data["owner"], sort=data["sort"])
        channel.save()
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)
        
    def add_to_channel(self, request, pk):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.get(id=pk)
        channel.users.add(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)

    def remove_from_channel(self, request, pk):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.get(id=pk)
        channel.users.remove(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)

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
from ej_profiles.models import Setting

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

    def add_to_general_channel(self, request, pk):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.get(id=pk)
        channel.users.add(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)

    def add_to_individual_channel(self, request):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.filter(owner=user, sort=data["sort"])[0]
        channel.users.add(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)

    def add_to_group_channel(self, request):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.filter(sort=data["sort"])[0]
        channel.users.add(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)


    def remove_from_individual_channel(self, request):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.filter(owner=user, sort=data["sort"])[0]
        channel.users.remove(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)

    def remove_from_general_channel(self, request, pk):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.get(id=pk)
        channel.users.remove(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)

    def check_user_channels(self, request, pk):
        data = request.data
        user = User.objects.get(id=pk)
        profile = user.profile
        settings = Setting.objects.get(profile=profile)
        channel_admin = models.Channel.objects.get(id=1)
        channel_mission = models.Channel.objects.get(id=2)
        channel_trophy = models.Channel.objects.filter(owner=user, sort="trophy").count()

        if(settings.mission_notifications == True):
            channel_mission.users.add(user)
        
        if(settings.admin_notifications == True):
            channel_admin.users.add(user)
        
        if(channel_trophy <=0):
            new_channel = models.Channel.objects.create(name="trophy channel", sort="trophy", owner=user)
            new_channel.users.add(user)
            new_channel.save()
            serializer = serializers.ChannelSerializer(new_channel)
            return Response(serializer.data)
        else: 
            return Response({"Usuário já adicionado nos canais!"})
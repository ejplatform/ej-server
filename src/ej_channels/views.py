from rest_framework import viewsets
from rest_framework.response import Response

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

    def add_to_general_channel(self, request):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.get(sort=data["sort"])
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

    def remove_from_general_channel(self, request):
        data = request.data
        user = User.objects.filter(id=data["user_id"])[0]
        channel = models.Channel.objects.get(sort=data["sort"])
        channel.users.remove(user)
        serializer = serializers.ChannelSerializer(channel)
        return Response(serializer.data)

    def check_user_channels(self, request, pk):
        user = User.objects.get(id=pk)
        # Get all channels that user can be added
        channel_admin = models.Channel.objects.get(sort="admin")
        channel_mission = models.Channel.objects.get(sort="mission")
        channel_trophy = models.Channel.objects.filter(owner=user, sort="trophy").count()
        channel_selected = models.Channel.objects.filter(owner=user, sort="selected").count()
        channel_press = models.Channel.objects.filter(owner=user, sort="press").count()
        # Add user on general channels
        channel_mission.users.add(user)
        channel_admin.users.add(user)
        # Verify every single user channel to add user
        if(channel_trophy <= 0):
            new_trophy_channel = models.Channel.objects.create(name="trophy channel", sort="trophy", owner=user)
            new_trophy_channel.users.add(user)
            new_trophy_channel.save()

        if(channel_selected <= 0):
            new_selected_channel = models.Channel.objects.create(name="selected channel", sort="selected", owner=user)
            new_selected_channel.users.add(user)
            new_selected_channel.save()

        if(channel_press <= 0):
            new_press_channel = models.Channel.objects.create(name="press channel", sort="press", owner=user)
            new_press_channel.users.add(user)
            new_press_channel.save()

        return Response({"Canais do usuário atualizados"})

from rest_framework import viewsets
from rest_framework.response import Response

from . import serializers
from . import models
from ej_channels.models import Channel


class MessageViewSet(viewsets.ViewSet):

    def index(self, request):
        queryset = models.Message.objects.all().order_by("-created_at")
        serializer = serializers.MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        channel = Channel.objects.get(id=data["channel_id"])
        message = models.Message(channel=channel, title=data["title"], body=data["body"], target=data["target"])
        message.save()
        serializer = serializers.MessageSerializer(message)
        return Response(serializer.data)

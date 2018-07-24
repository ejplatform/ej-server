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
from ej_channels.models import Channel

class MessageViewSet(viewsets.ViewSet):

    def index(self, request):
        queryset = models.Message.objects.all().order_by("-created_at")
        serializer = serializers.MessageSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        channel = Channel.objects.get(id=data["channel_id"])
        message = models.Message(channel=channel, title=data["title"], body=data["body"])
        message.save()
        serializer = serializers.MessageSerializer(message)
        return Response(serializer.data)
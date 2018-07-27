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
from ej_messages.models import Message

class NotificationViewSet(viewsets.ViewSet):

    def index(self, request):
        queryset = models.Notification.objects.all().order_by("-created_at")
        serializer = serializers.NotificationSerializer(queryset, many=True)
        return Response(serializer.data)

    def show(self, request, pk):
        queryset = models.Notification.objects.get(id=pk)
        serializer = serializers.NotificationSerializer(queryset)
        return Response(serializer.data)

    def create(self, request):
        data = request.data
        receiver = User.objects.get(id=data["receiver_id"])
        channel = Channel.objects.get(id=data["channel_id"])
        message = Message.objects.get(id=data["message_id"])
        notification = models.Notification(channel=channel, receiver=receiver, message=message)
        notification.save()
        serializer = serializers.NotificationSerializer(notification)
        return Response(serializer.data)
    
    def update_read(self, request):
        data = request.data
        notification = models.Notification.objects.get(id=data["notification_id"])
        notification.read = data["read"]
        notification.save()
        serializer = serializers.NotificationSerializer(notification)
        return Response(serializer.data)

    def user_notifications(self, request, pk):
        user = User.objects.get(id=pk)
        notifications = models.Notification.objects.all().order_by("-created_at")
        user_notifications = []
        for notification in notifications:
            if (notification.receiver.id == user.id):
                user_notifications.append(notification)

        serializer = serializers.NotificationSerializer(user_notifications, many=True)
        return Response(serializer.data)
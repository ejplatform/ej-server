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


class MissionForm(forms.Form):
    title = forms.CharField(max_length=50)

class MissionViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = models.Mission.objects.all()
        serializer = serializers.MissionSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        queryset = models.Mission.objects.filter(id=pk)[0]
        serializer = serializers.MissionSerializer(queryset)
        return Response(serializer.data)

    def create(self, request):
        print(request.POST)
        print(request.FILES)
        data = request.POST
        mission = models.Mission(title=data["title"], description=data["description"])
        mission.save()
        mission.fileUpload=request.FILES["coverFile"]
        mission.save()
        serializer = serializers.MissionSerializer(mission)
        return Response(serializer.data)

    def accept(self, request):
        data = json.loads(request.body.decode("utf8"))
        user = User.objects.filter(id=data["user_id"])[0]
        mission = models.Mission.objects.filter(id=data["id"])[0]
        mission.users.add(user)
        serializer = serializers.MissionSerializer(mission, context={'request': Request(request)})
        return Response(serializer.data)

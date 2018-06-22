from . import serializers
from . import models
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action

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
        print("ok")

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
        serializer = serializers.MissionSerializer(mission)
        return Response(serializer.data)

    def receipt(self, request, pk):
        data = request.POST
        mission = models.Mission.objects.filter(id=pk)[0]
        user = User.objects.filter(id=data["uid"])[0]
        receipt = models.Receipt(userName=data["userName"],
                                 userEmail=data["userEmail"],
                                 status=data["status"],
                                 description=data["description"],
                                 receiptFile=request.FILES["receiptFile"])
        receipt.user = user
        receipt.mission = mission
        receipt.save()
        # With a many to one relation, add receipt directly on mission.
        mission.receipt_set.add(receipt)
        serializer = serializers.MissionSerializer(mission)
        return Response(serializer.data)

    def receipts(self, request, pk):
        queryset = models.Mission.objects.filter(id=pk)[0].receipt_set.all()
        serializer = serializers.MissionReceiptSerializer(queryset, many=True)
        return Response(serializer.data)

    def user_status(self, request, mid, uid):
        mission = models.Mission.objects.filter(id=mid)[0]
        user = models.User.objects.filter(id=uid)[0]
        status = {"status": "new"}
        if (len(mission.users.all()) > 0 and user in mission.users.all()):
            status["status"] = "started";

        for receipt in mission.receipt_set.all():
            if (uid == str(receipt.user.id)):
             status["status"] = receipt.status

        return Response(status)

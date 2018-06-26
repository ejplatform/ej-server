from . import models
from ej_users.models import User
from rest_framework import serializers


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('display_name', 'id', 'email')

class MissionSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer(read_only=True)

    class Meta:
        model = models.Mission
        fields = ('id', 'title', 'description', 'users', 'fileUpload', 'owner')

class MissionReceiptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Receipt
        fields = ('id',
                  'userName',
                  'userEmail',
                  'status',
                  'description',
                  'receiptFile',
                  'user')


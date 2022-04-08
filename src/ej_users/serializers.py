from rest_framework import serializers
from .models import User


class UsersSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=50, min_length=5, required=True)
    email = serializers.EmailField(required=True)
    password_confirm = serializers.CharField(max_length=50, min_length=5, required=True)

    class Meta:
        model = User
        fields = ["id", "name", "email", "signature", "password", "password_confirm"]

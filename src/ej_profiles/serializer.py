from ej_profiles.models import Profile
from rest_framework import serializers


class ProfileSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11)

    class Meta:
        model = Profile
        fields = ["phone_number"]

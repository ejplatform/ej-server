from rest_framework import serializers
from .models import RasaConversation


class RasaConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RasaConversation
        fields = ["conversation", "domain"]

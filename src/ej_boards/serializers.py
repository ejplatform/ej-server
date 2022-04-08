from rest_framework import serializers
from .models import Board


class BoardSerializer(serializers.ModelSerializer):
    owner = serializers.SlugRelatedField(read_only=True, slug_field="email")

    class Meta:
        model = Board
        fields = ["title", "slug", "owner", "description"]

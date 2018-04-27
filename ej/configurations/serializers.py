from rest_framework import serializers

from .models import SocialMediaIcon, Color


class SocialMediaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SocialMediaIcon
        fields = ('id', 'url', 'name', 'link', 'priority', 'material_icon', 'fa_icon')


class ColorPalletSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Color
        fields = ('id', 'url', 'name', 'colors')

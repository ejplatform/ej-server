from rest_framework import serializers

from .models import SocialMedia, ColorPallete


class SocialMediaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ('id', 'url', 'name', 'link', 'priority', 'material_icon', 'fa_icon')


class ColorPalletSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ColorPallete
        fields = ('id', 'url', 'name', 'colors')

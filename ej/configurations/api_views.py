from rest_framework.viewsets import ModelViewSet

from .models import SocialMedia, Color
from .serializers import SocialMediaSerializer, ColorPalletSerializer


class SocialMediaViewSet(ModelViewSet):
    serializer_class = SocialMediaSerializer
    queryset = SocialMedia.objects.all()


class ColorPalletViewSet(ModelViewSet):
    serializer_class = ColorPalletSerializer
    queryset = Color.objects.all()

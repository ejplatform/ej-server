from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.http import JsonResponse

from .models import Profile
from .serializer import ProfileSerializer
from rest_framework.authtoken.models import Token


class ProfileViewSet(viewsets.ModelViewSet):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @action(detail=False, methods=["post"], url_path="set-phone-number")
    def set_phone_number(self, request):
        user = request.user
        profile = None
        try:
            profile = Profile.objects.get(user=user)
        except Exception as e:
            profile = Profile(user=user)
        phone_number = request.data.get("phone_number")
        if phone_number:
            profile.phone_number = phone_number
        profile.save()
        return JsonResponse({"phone_number": profile.phone_number})

    @action(detail=False, methods=["get"], url_path="phone-number")
    def phone_number(self, request):
        if request.user.is_authenticated:
            profile = Profile.objects.get(user=request.user)
            return JsonResponse({"phone_number": profile.phone_number})
        else:
            return Response(status=403)

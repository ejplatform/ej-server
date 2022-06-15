from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _

from .models import User, MetaData
from ej_profiles.models import Profile
from ej_users.serializers import UsersSerializer
from allauth.account.adapter import get_adapter


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    permission_classes_by_action = {"create": [AllowAny], "list": [IsAdminUser]}

    def create(self, request, pk=None):
        try:
            user = User.objects.get(email=request.data.get("email"))
            return self.get_user_token(user, request)
        except:
            return self.create_user(request)

    def create_user(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        user = serializer.create()
        token = Token.objects.create(user=user)
        self.check_user_metadata(user, request)
        self.check_profile(user, request)
        response = {"id": user.id, "name": user.name, "email": user.email, "token": token.key}
        return Response(response)

    def get_user_token(self, user, request):
        token, created = Token.objects.get_or_create(user=user)
        self.check_user_metadata(user, request)
        self.check_profile(user, request)
        return Response(
            {"token": token.key},
        )

    def check_profile(self, user, request):
        phone_number = request.data.get("phone_number", None)
        profile, created = Profile.objects.get_or_create(user=user)

        if phone_number:
            profile.phone_number = phone_number
            profile.save()

    def check_user_metadata(self, user, request):
        if not user.metadata_set.first():
            self.save_metadata(user, request)

    def save_metadata(self, user, request):
        metadata = request.data.get("metadata")
        if metadata:
            MetaData.objects.create(
                analytics_id=metadata.get("analytics_id"), mautic_id=metadata.get("mautic_id"), user=user
            )

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

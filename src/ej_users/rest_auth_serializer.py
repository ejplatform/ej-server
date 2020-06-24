from rest_framework import serializers
from .models import User, MetaData
try:
    from allauth.account import app_settings as allauth_settings
    from allauth.utils import (email_address_exists,
                               get_username_max_length)
    from allauth.account.adapter import get_adapter
    from allauth.account.utils import setup_user_email
    from allauth.socialaccount.helpers import complete_social_login
    from allauth.socialaccount.models import SocialAccount
    from allauth.socialaccount.providers.base import AuthProcess
    from django.utils.translation import gettext as _
except Exception as e:
    raise ImportError("allauth needs to be added to INSTALLED_APPS.")


class RegistrationSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=50,
        min_length=5,
        required=True
    )
    email = serializers.EmailField()

    def save(self, request):
        try:
            user = User.objects.get(email=request.data.get('email'))
            self.check_metadata(user, request)
            return user
        except Exception as e:
            pass
        email = request.data.get('email')
        name = request.data.get('name')
        user = User.objects.create_user(email=email, name=name)
        self.save_metadata(user, request)
        return user

    def check_metadata(self, user, request):
        if(not user.metadata_set.first()):
            self.save_metadata(user, request)

    def save_metadata(self, user, request):
        metadata = request.data.get('metadata')
        if(metadata):
            MetaData.objects.create(analytics_id=metadata.get('analytics_id'),
                                    mautic_id=metadata.get('mautic_id'),
                                    user=user)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        return email

    def validate_password1(self, password):
        return get_adapter().clean_password(password)

    def validate(self, data):
        return data

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', '')
        }

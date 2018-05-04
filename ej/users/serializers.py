from allauth.account import app_settings as allauth_settings
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.socialaccount.helpers import complete_social_login
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from requests.exceptions import HTTPError
from rest_auth.registration.serializers import SocialLoginSerializer, RegisterSerializer
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'image', 'name', 'email', 'biography', 'city',
                  'state', 'country', 'username', 'race', 'gender', 'tour_step',
                  'occupation', 'age', 'political_movement', 'is_superuser',)


class RegistrationSerializer(RegisterSerializer):
    name = serializers.CharField()
    tour_step = serializers.CharField()

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'name': self.validated_data.get('name', ''),
            'tour_step': self.validated_data.get('tour_step', ''),
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', '')
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)

        self.cleaned_data = self.get_cleaned_data()
        user.name = self.cleaned_data.get('name')
        user.tour_step = self.cleaned_data.get('tour_step')

        adapter.save_user(request, user, self)

        self.custom_signup(request, user)
        setup_user_email(request, user, [])

        return user

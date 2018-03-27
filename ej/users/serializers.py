from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from rest_framework import routers, serializers, viewsets
from rest_auth.registration.serializers import SocialLoginSerializer, RegisterSerializer
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email
from allauth.account import app_settings as allauth_settings
from allauth.socialaccount.helpers import complete_social_login
from requests.exceptions import HTTPError

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'image', 'name', 'email', 'biography', 'city',
                  'state', 'country', 'username', 'race', 'gender','tour_step',
                  'occupation', 'age', 'political_movement', 'is_superuser', )



class RegistrationSerializer(RegisterSerializer):
    name = serializers.CharField()
    tour_step = serializers.CharField()

    def get_cleaned_data(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'name': self.validated_data.get('name', ''),
            'tour_step':  self.validated_data.get('tour_step', ''),
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

class FixSocialLoginSerializer(SocialLoginSerializer):
    def validate(self, attrs):

        request = self._get_request()

        view = self.get_view()
        adapter = self.get_adapter(request, view)

        app = adapter.get_provider().get_app(request)

        access_token = self.get_token(adapter, app, attrs, request, view)

        social_token = adapter.parse_token({'access_token': access_token})
        social_token.app = app

        try:
            login = self.get_social_login(adapter, app, social_token, access_token)
            complete_social_login(request, login)
        except HTTPError:
            raise serializers.ValidationError(_('Incorrect value'))

        self.validate_social_email_existence(login, request)

        attrs['user'] = login.account.user

        return attrs

    def validate_social_email_existence(self, login, request):
        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            if (allauth_settings.UNIQUE_EMAIL):
                email_exists = get_user_model().objects.filter(email=login.user.email).exists()
                if login.user.email and email_exists:
                    # There is an account already
                    raise serializers.ValidationError(
                        _("A user is already registered with this e-mail address."))

            login.lookup()
            login.save(request, connect=True)

    def get_token(self, adapter, app, attrs, request, view):
        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token
        # Case 1: We received the access_token
        if attrs.get('access_token'):
            access_token = attrs.get('access_token')

        # Case 2: We received the authorization code
        elif attrs.get('code'):
            self.client_class = self.get_attribute(view, 'client_class')
            self.callback_url = self.get_attribute(view, 'callback_url')

            code = attrs.get('code')
            token = self.generate_token(adapter, app, code, request)

            access_token = token['access_token']

        else:
            raise serializers.ValidationError(
                _("Incorrect input. access_token or code is required."))
        return access_token

    def generate_token(self, adapter, app, code, request):
        provider = adapter.get_provider()
        scope = provider.get_scope(request)
        client = self.client_class(
            request,
            app.client_id,
            app.secret,
            adapter.access_token_method,
            adapter.access_token_url,
            self.callback_url,
            scope
        )
        token = client.get_access_token(code)
        return token

    def get_adapter(self, request, view):
        adapter_class = self.get_attribute(view, "adapter_class")
        adapter = adapter_class(request)
        return adapter

    def get_view(self):
        view = self.context.get('view')
        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable")
            )
        return view

    def get_attribute(self, view, attribute_name):

        attribute = getattr(view, attribute_name, None)

        if attribute:
            return attribute
        else:
            raise serializers.ValidationError(
                _("Define " + attribute_name + " in view")
            )

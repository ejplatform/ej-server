from django.utils.translation import ugettext_lazy as _
from django.conf.urls import url, include
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import routers, serializers, viewsets
from rest_auth.registration.serializers import SocialLoginSerializer
from allauth.account import app_settings as allauth_settings
from allauth.socialaccount.helpers import complete_social_login
from requests.exceptions import HTTPError

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'image', 'name', 'email', 'biography', 'city',
                  'state', 'country', 'username', 'race', 'gender',
                  'occupation', 'age', 'political_movement', 'is_superuser', )


class FixSocialLoginSerializer(SocialLoginSerializer):
        def validate(self, attrs):
            view = self.context.get('view')
            request = self._get_request()

            if not view:
                raise serializers.ValidationError(
                    _("View is not defined, pass it as a context variable")
                )

            adapter_class = getattr(view, 'adapter_class', None)
            if not adapter_class:
                raise serializers.ValidationError(_("Define adapter_class in view"))

            adapter = adapter_class(request)
            app = adapter.get_provider().get_app(request)

            # More info on code vs access_token
            # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

            # Case 1: We received the access_token
            if attrs.get('access_token'):
                access_token = attrs.get('access_token')

            # Case 2: We received the authorization code
            elif attrs.get('code'):
                self.callback_url = getattr(view, 'callback_url', None)
                self.client_class = getattr(view, 'client_class', None)

                if not self.callback_url:
                    raise serializers.ValidationError(
                        _("Define callback_url in view")
                    )
                if not self.client_class:
                    raise serializers.ValidationError(
                        _("Define client_class in view")
                    )

                code = attrs.get('code')

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
                access_token = token['access_token']

            else:
                raise serializers.ValidationError(
                    _("Incorrect input. access_token or code is required."))

            social_token = adapter.parse_token({'access_token': access_token})
            social_token.app = app

            try:
                login = self.get_social_login(adapter, app, social_token, access_token)
                complete_social_login(request, login)
            except HTTPError:
                raise serializers.ValidationError(_('Incorrect value'))

            if not login.is_existing:
                # We have an account already signed up in a different flow
                # with the same email address: raise an exception.
                # This needs to be handled in the frontend. We can not just
                # link up the accounts due to security constraints
                if(allauth_settings.UNIQUE_EMAIL):
                    if login.user.email and get_user_model().objects.filter(
                        email=login.user.email,
                    ).exists():
                        # There is an account already
                        raise serializers.ValidationError(
                        _("A user is already registered with this e-mail address."))

                login.lookup()
                login.save(request, connect=True)
            attrs['user'] = login.account.user

            return attrs

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class FacebookLogin(SocialLoginView):
   adapter_class = FacebookOAuth2Adapter
   client_class = OAuth2Client
   callback_url = 'http://localhost:8000'

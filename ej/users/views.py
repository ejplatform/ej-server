from allauth.account import views as allauth_views
from allauth.account.forms import LoginForm
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse, HttpResponse
from django.urls import reverse
from django.views.generic import RedirectView, UpdateView
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from rest_auth.registration.views import SocialLoginView
from rest_auth.social_serializers import TwitterLoginSerializer
from rest_auth.views import LoginView
from rest_framework import status
from rest_framework.authtoken.models import Token

from .models import User


@method_decorator(xframe_options_exempt, name='dispatch')
class SignupView(allauth_views.SignupView):
    template_name = 'account/login-signup.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        return super().get_context_data(login_form=LoginForm(), **kwargs)

    def get_success_url(self):
        return self.success_url


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('user-detail',
                       kwargs={'pk': self.request.user.id})


class UserUpdateView(LoginRequiredMixin, UpdateView):
    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('user-detail',
                       kwargs={'pk': self.request.user.id})

    def get_object(self, queryset=None):
        # Only get the User record for the user making the request
        queryset = User.objects if queryset is None else queryset
        return queryset.get(username=self.request.user.username)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class TwitterLogin(LoginView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter


def get_api_key(request):
    if request.user.id is None:
        raise Http404

    token = Token.objects.get_or_create(user=request.user)
    return JsonResponse({'key': token[0].key}, status=status.HTTP_200_OK)


# This view exists only to help reset sessionid and csrftoken cookies on the client browser
# Javascript can't do it itself because csrftoken was previously HTTP_ONLY
# This cookie needs to be js accessible to allow for CSRF protection on XHR requests
# FIXME: this view must be deleted when no more users have csrftoken cookies protected by HTTP_ONLY setting
def clean_cookies(request):
    response = HttpResponse()
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')
    return response

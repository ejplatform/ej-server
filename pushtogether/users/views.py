from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework import status

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User

from allauth.account.views import SignupView
from allauth.account.forms import LoginForm
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from rest_auth.views import LoginView
from rest_auth.registration.views import SocialLoginView
from rest_auth.social_serializers import TwitterLoginSerializer

from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @detail_route(methods=['POST'])
    @parser_classes((FormParser, MultiPartParser))
    def image(self, request, *args, **kwargs):
        if 'image' in request.data:
            user_profile = self.get_object()
            user_profile.image.delete()

            upload = request.data['image']

            user_profile.image.save(upload.name, upload)

            return Response(status=status.HTTP_201_CREATED,
                            headers={'Location': user_profile.image.url})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LoginSignupView(SignupView):

    template_name = 'account/login-signup.html'
    success_url = '/users/close'

    def get_context_data(self, **kwargs):
        # we get context data from original view
        context = super(LoginSignupView,
                        self).get_context_data(**kwargs)
        context['login_form'] = LoginForm() # add form to context
        return context


    def get_success_url(self):
        return self.success_url


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class TwitterLogin(LoginView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter

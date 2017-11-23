from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import detail_route, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework import permissions

from django.http import Http404, JsonResponse
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User
from .permissions import IsCurrentUserOrAdmin

from allauth.account.views import SignupView
from allauth.account.forms import LoginForm
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from rest_auth.views import LoginView
from rest_auth.registration.views import SocialLoginView
from rest_auth.social_serializers import TwitterLoginSerializer

from .serializers import UserSerializer, FixSocialLoginSerializer


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

    def retrieve(self, request, pk=None):
        if self.request.user.id is None:
            raise Http404

        serializer = UserSerializer(self.request.user)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [permissions.IsAdminUser, ]
        elif self.action == 'retrieve':
            self.permission_classes = [IsCurrentUserOrAdmin]
        return super(self.__class__, self).get_permissions()


class LoginSignupView(SignupView):

    template_name = 'account/login-signup.html'
    success_url = '/api/profile/close'

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
        return reverse('users:user-detail',
                       kwargs={'pk': self.request.user.id})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:user-detail',
                       kwargs={'pk': self.request.user.id})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    serializer_class = FixSocialLoginSerializer


class TwitterLogin(LoginView):
    serializer_class = TwitterLoginSerializer
    adapter_class = TwitterOAuthAdapter


def get_api_key(request):
    if request.user.id is None:
            raise Http404

    token = Token.objects.get_or_create(user=request.user)
    return JsonResponse({ 'key': token[0].key }, status=200)

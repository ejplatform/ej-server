from rest_framework.viewsets import ModelViewSet

from django.core.urlresolvers import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User

from allauth.account.views import SignupView
from allauth.account.forms import LoginForm
from allauth.socialaccount.views import SocialLogin

from .serializers import UserSerializer

class UserViewSet(ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


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


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


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


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'

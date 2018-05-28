import logging

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from . import forms

User = get_user_model()
urlpatterns = Router(
    template='ej_accounts/{name}.jinja2',
)

log = logging.getLogger('ej')


@urlpatterns.route('register/')
def register(request):
    form = forms.RegistrationForm()

    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            name, email, password = data['name'], data['email'], data['password']
            try:
                user = User.objects.create_user(username, email, password, name=name)
                log.info(f'user {user} ({email}) successfully created')
            except IntegrityError as ex:
                log.info(f'invalid login attempt: {email}')
                form.add_error(None, str(ex))
            else:
                user = auth.authenticate(request,
                                         username=user.username,
                                         password=password)
                auth.login(request, user)
                log.info(f'user {user} ({email}) logged in')
                return redirect(request.GET.get('next', '/'))

    return {'user': request.user, 'form': form}


@urlpatterns.route('login/')
def login(request):
    form = forms.LoginForm(request.POST if request.method == 'POST' else None)
    error_msg = _('Invalid username or password')
    next = request.GET.get('next', '/')
    fast = request.GET.get('fast', 'false') == 'true'

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        email, password = data['email'], data['password']

        try:
            user = User.objects.get_by_email_or_username(email)
            user = auth.authenticate(request, username=user.username, password=password)
            log.info(f'user {user} ({email}) successfully authenticated')
            auth.login(request, user)
            if user is None:
                raise User.DoesNotExist
        except User.DoesNotExist:
            log.info(f'invalid login attempt: {email}')
            form.add_error(None, error_msg)
        else:
            return redirect(next)
    elif fast and request.user.is_authenticated and next:
        return redirect(next)

    return {'user': request.user, 'form': form}


@urlpatterns.route('logout/', login=True)
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('/')
    return HttpResponseServerError('must use POST to logout')


@urlpatterns.route('profile/recover-password/', login=True)
def recover_password(request):
    return {
        'user': request.user,
        'profile': request.user.profile,
    }


@urlpatterns.route('profile/reset-password/', login=True)
def recover_password(request):
    return {
        'user': request.user,
        'profile': request.user.profile,
    }


@urlpatterns.route('profile/remove/', login=True)
def remove_account(request):
    return {
        'user': request.user,
        'profile': request.user.profile,
    }

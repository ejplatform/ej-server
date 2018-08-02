import logging

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import Http404, JsonResponse, HttpResponse
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.authtoken.models import Token

from boogie.router import Router
from ej_users import forms
from ej_users.models import User
from ej_channels.models import Channel
from ej_notifications.models import Notification

User = get_user_model()

app_name = 'ej_users'
urlpatterns = Router(
    template='ej_users/{name}.jinja2',
    models={
        'user': User,
    },
    lookup_field='username',
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
            if user is None:
                raise User.DoesNotExist
            auth.login(request, user, backend=user.backend)
        except User.DoesNotExist:
            log.info(f'invalid login attempt: {email}')
            form.add_error(None, error_msg)
        else:
            return redirect(next)
    elif fast and request.user.is_authenticated and next:
        return redirect(next)

    return {'user': request.user, 'form': form}


@urlpatterns.route('logout/')
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('home')
    return HttpResponseServerError('cannot logout using a GET')


@urlpatterns.route('profile/recover-password/')
def recover_password(request):
    return {
        'user': request.user,
    }


@urlpatterns.route('profile/reset-password/', login=True)
def reset_password(request):
    return {
        'user': request.user,
        'profile': request.user.profile,
    }


@urlpatterns.route('profile/remove/', login=True)
def remove_account(request):
    if request.method == 'POST':
        user = request.user
        if request.POST.get('remove_account', False) == 'true':
            user.is_active = False
            user.delete()
            return redirect('home')
        else:
            return HttpResponseServerError('invalid POST request')
    return {
        'user': request.user,
        'profile': request.user.profile,
    }


#
# Registration via API + cookies
#
@urlpatterns.route('key/')
def api_key(request):
    if request.user.id is None:
        raise Http404
    token = Token.objects.get_or_create(user=request.user)
    return JsonResponse({'key': token[0].key}, status=status.HTTP_200_OK)


# FIXME: this view must be deleted when no more users have csrftoken cookies protected by HTTP_ONLY setting
@urlpatterns.route('reset/')
def clean_cookies():
    # This view exists only to help reset sessionid and csrftoken cookies on
    # the client browser. Javascript can't do it itself because csrftoken was
    # previously HTTP_ONLY. This cookie needs to be js accessible to allow for
    # CSRF protection on XHR requests

    response = HttpResponse()
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')
    return response

@urlpatterns.get('check-token', csrf=False)
def check_token(request):
    token_to_validate = request.META['HTTP_AUTHORIZATION'].split(' ')[1]
    token = Token.objects.filter(key=token_to_validate)
    if (len(token) > 0):
        return JsonResponse({"expired": False})
    return JsonResponse({"expired": True})

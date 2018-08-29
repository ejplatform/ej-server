import logging

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.authtoken.models import Token

from boogie.router import Router
from ej_users import forms
from .socialbuttons import social_buttons

User = get_user_model()

app_name = 'ej_users'
urlpatterns = Router(
    template='ej_users/{name}.jinja2',
)
log = logging.getLogger('ej')


@urlpatterns.route('register/')
def register(request):
    if not request.user.is_authenticated:
        form = forms.RegistrationForm()

        if request.method == 'POST':
            form = forms.RegistrationForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                name, email, password = data['name'], data['email'], data['password']
                try:
                    user = User.objects.create_user(email, password, name=name)
                    log.info(f'user {user} ({email}) successfully created')
                except IntegrityError as ex:
                    log.info(f'invalid login attempt: {email}')
                    form.add_error(None, str(ex))
                else:
                    user = auth.authenticate(request,
                                             email=user.email,
                                             password=password)
                    auth.login(request, user)
                    log.info(f'user {user} ({email}) logged in')
                    return redirect(request.GET.get('next', '/'))

        return {
            'user': request.user,
            'form': form,
            'social_buttons': social_buttons(request),
        }
    else:
        return redirect(request.GET.get('next', '/profile/'))


@urlpatterns.route('login/')
def login(request, redirect_to='/'):
    form = forms.LoginForm(request.POST if request.method == 'POST' else None)
    error_msg = _('Invalid email or password')
    next = request.GET.get('next', redirect_to)
    fast = request.GET.get('fast', 'false') == 'true' or 'fast' in request.GET

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        email, password = data['email'], data['password']

        try:
            user = User.objects.get_by_email(email)
            user = auth.authenticate(request, email=user.email, password=password)
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

    return {
        'user': request.user,
        'form': form,
        'login_extra': login_extra_template.render(request=request),
        'social_buttons': social_buttons(request),
    }


@urlpatterns.route('logout/')
def logout(request):
    if request.method == 'POST' and request.user.id:
        auth.logout(request)
        return redirect(settings.EJ_ANONYMOUS_HOME_PATH)
    return HttpResponseServerError()


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
            return redirect(settings.EJ_ANONYMOUS_HOME_PATH)
        else:
            return HttpResponseServerError('invalid POST request')
    return {
        'user': request.user,
        'profile': request.user.profile,
    }


#
# Registration via API + cookies
#
@urlpatterns.route('profile/api-key/')
def api_key(request):
    if request.user.id is None:
        raise Http404
    token = Token.objects.get_or_create(user=request.user)
    return JsonResponse({'key': token[0].key}, status=status.HTTP_200_OK)


#
# Auxiliary functions and templates
#
login_extra_template = get_template('socialaccount/snippets/login_extra.html')

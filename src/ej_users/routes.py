import logging
import os

from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.template.loader import get_template
from django.utils.translation import ugettext_lazy as _
from jinja2 import FileSystemLoader, Environment
from rest_framework import status
from rest_framework.authtoken.models import Token

from boogie.router import Router
from . import forms
from .models import PasswordResetToken, generate_token
from .socialbuttons import social_buttons

User = get_user_model()

app_name = 'ej_users'
urlpatterns = Router(
    template='ej_users/{name}.jinja2',
    models={
        'token': PasswordResetToken,
    },
    lookup_field={'token': 'url'}

)
log = logging.getLogger('ej')


@urlpatterns.route('register/')
def register(request):
    form = forms.RegistrationForm.bind(request)
    next_url = request.GET.get('next', '/')

    if form.is_valid_post():
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
            return redirect(next_url)

    return {
        'user': request.user,
        'form': form,
        'social_js': login_extra_template.render(request=request),
        'social_buttons': social_buttons(request),
    }


@urlpatterns.route('login/')
def login(request, redirect_to='/'):
    form = forms.LoginForm.bind(request)
    error_msg = _('Invalid email or password')
    next_url = request.GET.get('next', redirect_to)
    fast = request.GET.get('fast', 'false') == 'true' or 'fast' in request.GET

    if form.is_valid_post():
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
            return redirect(next_url)

    elif fast and request.user.is_authenticated and next_url:
        return redirect(next_url)

    return {
        'user': request.user,
        'form': form,
        'next': next_url,
        'social_js': login_extra_template.render(request=request),
        'social_buttons': social_buttons(request),
    }


@urlpatterns.route('logout/')
def logout(request):
    if request.method == 'POST' and request.user.id:
        auth.logout(request)
        return redirect(settings.EJ_ANONYMOUS_HOME_PATH)
    return HttpResponseServerError()


@urlpatterns.route('reset-password/<model:token>/')
def reset_password(request, token):
    form = None
    next_url = request.GET.get('next', '/login/')
    user = token.user

    if not (token.is_expired or token.is_used):
        form = forms.ResetPasswordForm.bind(request)
        if request.method == 'POST' and form.is_valid():
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            token.delete()
            return redirect(next_url)

    return {
        'user': user,
        'form': form,
        'isExpired': token.is_expired,
    }


@urlpatterns.route('recover-password/')
def recover_password(request):
    form = forms.RecoverPasswordForm(request.POST or None)

    dirname = os.path.dirname(__file__)
    template_dir = os.path.join(dirname, 'jinja2/ej_users')

    loader = FileSystemLoader(searchpath=template_dir)
    environment = Environment(loader=loader)
    template_file = "recover-password-message.jinja2"
    template = environment.get_template(template_file)
    user = None
    success = False

    if request.method == "POST" and form.is_valid():
        success = True
        if User.objects.filter(email=form.cleaned_data['email']).exists():
            if settings.HOSTNAME == 'localhost':
                host = 'http://localhost:8000'

            else:
                host = 'http://' + settings.HOSTNAME

            user = User.objects.get_by_email(request.POST['email'])
            token = generate_token(user)
            from_email = settings.DEFAULT_FROM_EMAIL
            template_message = template.render({'link': host + '/reset-password/' + token.url})
            send_mail(_("Please reset your password"), template_message,
                      from_email, [request.POST['email']],
                      fail_silently=False)

    return {
        'user': user,
        'form': form,
        'success': success,

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

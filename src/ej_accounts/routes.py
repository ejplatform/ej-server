import logging

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.http import HttpResponseServerError
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from boogie.router import Router
from . import forms

urlpatterns = Router()
User = get_user_model()

log = logging.getLogger('ej')


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

    ctx = dict(user=request.user, form=form)
    return render(request, 'pages/login.jinja2', ctx)


@urlpatterns.route('logout/', login=True)
def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        return redirect('/')
    return HttpResponseServerError('must use POST to logout')


@urlpatterns.route('leave/', login=True)
def leave(request):
    ctx = dict(
        content_html='<h1>Error</h1><p>Not implemented yet!</p>'
    )
    return render(request, 'base.jinja2', ctx)


@urlpatterns.route('register/')
def register(request):
    form = forms.RegistrationForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        name, email, password = data['name'], data['email'], data['password']
        try:
            user = User.objects.create_simple_user(name, email, password)
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

    ctx = dict(user=request.user, form=form)
    return render(request, 'pages/register.jinja2', ctx)

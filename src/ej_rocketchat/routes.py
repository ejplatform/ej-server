from logging import getLogger

from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse

from boogie.router import Router
from ej_users.routes import login as ej_login
from . import forms
from .decorators import security_policy, requires_rc_perm
from .models import RCConfig, RCAccount
from .rocket import rocket

log = getLogger('ej')
app_name = 'ej_rocketchat'
urlpatterns = Router(
    template=['ej_rocketchat/{name}.jinja2'],
)


@urlpatterns.route('', decorators=[requires_rc_perm, security_policy])
def iframe(request):
    if request.user.is_superuser:
        if request.GET.get('admin-login') != 'true':
            return redirect('rocket:ask-admin-password')
        token = rocket.admin_token
    else:
        account = rocket.find_or_create_account(request.user)
        if account is None:
            return redirect('rocket:register')
        token = account.auth_token

    return {
        'rocketchat_url': rocket.url,
        'auth_token': token,
        'auth_token_repr': repr(token),
    }


@urlpatterns.route('register/', decorators=[requires_rc_perm, security_policy])
def register(request):
    if RCAccount.objects.filter(user=request.user).exists():
        return redirect('rocket:iframe')
    if request.method == 'POST':
        form = forms.CreateUsernameForm(request.POST, user=request.user)
        if form.is_valid():
            return redirect('rocket:iframe')
    else:
        form = forms.CreateUsernameForm(user=request.user)
    return {'form': form}


@urlpatterns.route('ask-password/', decorators=[requires_rc_perm, security_policy])
def ask_admin_password(request):
    if not request.user.is_superuser:
        raise Http404
    if request.method == 'POST':
        form = forms.AskAdminPasswordForm(request.POST)
        if form.is_valid():
            url = reverse('rocket:iframe')
            return redirect(f'{url}?admin-login=true')
    else:
        form = forms.AskAdminPasswordForm()
    return {'form': form}


@urlpatterns.route('config/', decorators=[security_policy])
def config(request):
    if not request.user.is_superuser:
        raise Http404

    config = RCConfig.objects.default_config(raises=False)
    form_kwargs = {}
    if config:
        form_kwargs['data'] = {'rocketchat_url': config.url}

    if request.method == 'POST':
        form = forms.RocketIntegrationForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            username = form.cleaned_data['username']
            rocket.password_login(username, password)
            url = reverse('rocket:iframe')
            return redirect(f'{url}??admin-login=true')
    else:
        form = forms.RocketIntegrationForm(**form_kwargs)
    return {'form': form}


@urlpatterns.route('intro/', login=True, decorators=[security_policy])
def intro():
    return {}


@urlpatterns.route('login/',
                   decorators=[security_policy],
                   template='ej_users/login.jinja2')
def login(request):
    log.info(f'login attempt via /talks/login: {request.user}')
    if request.user.is_authenticated:
        return redirect(request.GET.get('next', ['/talks/'])[0])
    return ej_login(request)


@urlpatterns.route('check-login/',
                   decorators=[security_policy])
def check_login(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.user.is_superuser:
        auth_token = rocket.admin_token
    else:
        auth_token = rocket.login_token(request.user)
    return JsonResponse({'loginToken': auth_token})

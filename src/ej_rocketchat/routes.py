from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect
from django.urls import reverse

from boogie.router import Router
from . import forms
from .decorators import security_policy, requires_rc_perm
from .models import RCConfig, RCAccount
from .rocket import rocket

app_name = 'ej_rocketchat'
urlpatterns = Router(
    template=['ej_rocketchat/{name}.jinja2'],
)


@urlpatterns.route('', decorators=[requires_rc_perm])
def iframe(request):
    if request.user.is_superuser:
        if request.GET.get('admin-login') != 'true':
            return redirect('rocket:ask-admin-password')
    else:
        account = rocket.find_or_create_account(request.user)
        if account is None:
            return redirect('rocket:register')
    return {'rocketchat_url': rocket.url}


@urlpatterns.route('register/', decorators=[requires_rc_perm])
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


@urlpatterns.route('ask-password/', decorators=[requires_rc_perm])
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


@urlpatterns.route('config/')
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


@urlpatterns.route('intro/', login=True)
def intro():
    return {}


@urlpatterns.route('check-login/',
                   csrf=False,
                   xframe=False,
                   decorators=[security_policy])
def check_login(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.user.is_superuser:
        auth_token = rocket.admin_token
    else:
        auth_token = rocket.login_token(request.user)
    return JsonResponse({'loginToken': auth_token})

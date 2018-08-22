from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect

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
    account = rocket.find_or_create_account(request.user)
    if account is None:
        return redirect('rocket:register')
    rocket.login(request.user)
    return {'rocketchat_url': rocket.url}


@urlpatterns.route('register/', decorators=[requires_rc_perm])
def register(request):
    if request.method == 'POST':
        form = forms.CreateUsernameForm(request.POST, user=request.user)
        if form.is_valid():
            return redirect('rocket:iframe')
    else:
        form = forms.CreateUsernameForm(user=request.user)
    return {'form': form}


@urlpatterns.route('config/')
def config(request):
    if not request.user.is_superuser:
        raise Http404

    config_data = RCConfig.objects.default_config(raises=False)
    if config_data:
        config_data = {
            'rocketchat_url': config_data.url,
            'admin_username': 'admin',
            'admin_password': '',
        }

    if request.method == 'POST':
        form = forms.RocketIntegrationForm(request.POST)
        if form.is_valid():
            form.get_config()
            return redirect('/')
    else:
        form = forms.RocketIntegrationForm(config_data)
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
    auth_token = rocket.login_token(request.user)
    return JsonResponse({'loginToken': auth_token})

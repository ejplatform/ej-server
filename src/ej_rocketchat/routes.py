from constance import config
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from boogie.router import Router
from . import helpers
from .decorators import custom_headers


app_name = 'ej_rocketchat'
urlpatterns = Router()


@urlpatterns.route('', login=True)
def index(request):
    ctx = dict(
        rocketchat_url=config.ROCKETCHAT_URL,
    )
    return render(request, 'pages/rocket.jinja2', ctx)


@urlpatterns.route('intro/', login=True)
def intro(request):
    return render(request, 'pages/rocket-intro.jinja2')


@urlpatterns.route('check-login/', csrf=False, xframe=False, decorators=[custom_headers])
def check_login(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    name = request.user.name.strip()
    login_token = helpers.create_rc_user_token(
        request.user.email,
        name or request.user.username,
        request.user.username
    )
    return JsonResponse({'loginToken': login_token})


@urlpatterns.route('redirect/', csrf=False, xframe=False, decorators=[custom_headers])
def rocket_redirect(request):
    return redirect(config.ROCKETCHAT_URL)

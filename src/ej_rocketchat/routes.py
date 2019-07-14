from logging import getLogger

from boogie.router import Router
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect, render

from ej_users.routes import login as ej_login
from . import forms
from .decorators import security_policy, requires_rc_perm
from .models import RCConfig, RCAccount, CAN_LOGIN_PERM
from .rocket import rocket

log = getLogger("ej")
app_name = "ej_rocketchat"
urlpatterns = Router(template=["ej_rocketchat/{name}.jinja2"])


@urlpatterns.route("", decorators=[security_policy])
def index(request):
    base_url = request.scheme + "://" + request.get_host()

    if not request.user.has_perm(CAN_LOGIN_PERM):
        return render(request, "ej_rocketchat/forbidden.jinja2")

    # Superuser must type the password since it is not stored in the database
    if not rocket.has_config:
        if request.user.is_superuser:
            return redirect("rocket:config")
        return render(request, "ej_rocketchat/forbidden.jinja2")
    elif request.user.is_superuser:
        form = forms.AskAdminPasswordForm(request=request)
        if not form.is_valid_post():
            return {
                "rocketchat_url": rocket.url,
                "username": rocket.admin_username,
                "token": rocket.admin_token,
                "form": form,
                "base_url": base_url,
            }
    else:
        account = rocket.find_or_create_account(request.user)
        if account is None:
            return redirect("rocket:register")

    ctx = {"url": rocket.url + "/home/", "url_escape": repr(rocket.url + "/home/"), "base_url": base_url}
    return render(request, "ej_rocketchat/redirect.jinja2", ctx)


@urlpatterns.route("register/", decorators=[requires_rc_perm])
def register(request):
    if RCAccount.objects.filter(user=request.user).exists():
        return redirect("rocket:index")

    form = forms.CreateUsernameForm(request=request, user=request.user)
    if form.is_valid_post():
        return redirect("rocket:index")
    return {"form": form}


@urlpatterns.route("config/")
def config(request):
    if not request.user.is_superuser:
        raise Http404

    cfg = RCConfig.objects.default_config(raises=False)
    form_kwargs = {}
    if cfg:
        form_kwargs["data"] = {"rocketchat_url": cfg.url}
    form = forms.RocketIntegrationForm(request=request, **form_kwargs)

    if form.is_valid_post():
        password = form.cleaned_data["password"]
        username = form.cleaned_data["username"]
        rocket.password_login(username, password)
        return redirect("rocket:index")

    return {"form": form}


@urlpatterns.route("intro/", login=False, decorators=[security_policy])
def intro(request):
    base_url = request.scheme + "://" + request.get_host()
    return {"base_url": base_url}


@urlpatterns.route("login/", decorators=[security_policy], template="ej_users/login.jinja2")
def login(request):
    log.info(f"login attempt via /talks/login: {request.user}")
    if request.user.is_authenticated:
        return redirect(request.GET.get("next", ["/talks/"])[0])
    return ej_login(request, redirect_to="/talks/")


@urlpatterns.route("api-login/", decorators=[security_policy])
def check_login(request):
    if not request.user.is_authenticated:
        log.warning(f"Rocket.Chat: anonymous user login attempt.")
        return HttpResponse(status=401)

    auth_token = rocket.get_auth_token(request.user)
    log.info(f"Rocket.Chat: {request.user} attempted login")
    return JsonResponse({"loginToken": auth_token})

from logging import getLogger

from boogie.router import Router
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import ugettext as _

from ej_users.forms import LoginForm
from ej_users.routes import social_js_template
from ej_users.socialbuttons import social_buttons
from . import forms
from .decorators import security_policy, requires_rc_perm
from .models import RCConfig, RCAccount, CAN_LOGIN_PERM
from .rocket import new_config

log = getLogger("ej")
app_name = "ej_rocketchat"
urlpatterns = Router(template=["ej_rocketchat/{name}.jinja2"])


@urlpatterns.route("", decorators=[security_policy])
def index(request):
    rocket = new_config()
    base_url = request.scheme + "://" + request.get_host()
    user = request.user

    if user.is_superuser and not rocket.has_config:
        cfg = RCConfig.objects.default_config(raises=False)
        form = forms.RocketIntegrationForm(request=request)
        form.fields["rocketchat_url"].initial = getattr(cfg, "url", "http://localhost:3000")

        if form.is_valid_post():
            form.save()
            return redirect(rocket.url)

        return render(request, "ej_rocketchat/config.jinja2", {"form": form})

    elif not rocket.has_config or not user.has_perm(CAN_LOGIN_PERM):
        return render(request, "ej_rocketchat/forbidden.jinja2")

    elif user.is_superuser:
        return redirect(rocket.url)

    elif not RCAccount.objects.filter(user=user).exists():
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


@urlpatterns.route("intro/", login=False, decorators=[security_policy])
def intro(request):
    base_url = request.scheme + "://" + request.get_host()
    return {"base_url": base_url}


@urlpatterns.route("login/", decorators=[security_policy])
def login(request):
    rocket = new_config()
    form = LoginForm(request=request)
    error_msg = _("Invalid email or password")
    user = request.user
    auth_token = None

    if user.is_superuser:
        auth_token = rocket.renew_admin_token()
    elif user.has_perm(CAN_LOGIN_PERM):
        if RCAccount.objects.filter(user=user).exists():
            auth_token = rocket.renew_auth_token(user)
        else:
            return redirect("rocket:register")
    elif user.is_authenticated:
        return render(request, "ej_rocketchat/forbidden.jinja2")
    elif form.is_valid_post():
        data = form.cleaned_data
        email, password = data["email"], data["password"]
        user_model = get_user_model()

        try:
            user = user_model.objects.get_by_email(email)
            user = auth.authenticate(request, email=user.email, password=password)
            if user is None:
                raise user_model.DoesNotExist
            auth.login(request, user, backend=user.backend)
            log.info(f"[Rocket.Chat Auth] user {user} ({email}) successfully authenticated")
            auth_token = rocket.get_auth_token(user)
        except user_model.DoesNotExist:
            form.add_error(None, error_msg)
            log.info(f"[Rocket.Chat Auth] invalid login attempt: {email}")

    return {
        "user": user,
        "next": None,
        "auth_token": auth_token,
        "talks_url": reverse("rocket:index"),
        "rocket_chat_url": rocket.url,
        "form": form,
        "social_js": social_js_template().render(request=request),
        "social_buttons": social_buttons(request),
    }


@urlpatterns.route("api-login/", decorators=[security_policy])
def api_login(request):
    user = request.user
    if not user.is_authenticated:
        log.warning(f"[rocket:api-login] anonymous user login attempt.")
        return HttpResponse(status=401)
    elif not user.has_perm(CAN_LOGIN_PERM) or (
        not user.is_superuser and not RCAccount.objects.filter(is_active=True, user=user).exists()
    ):
        log.warning(f"[rocket:api-login] forbidden login api-login attempt from {user}.")
        return HttpResponse(status=401)

    try:
        rocket = new_config()
        auth_token = rocket.get_auth_token(user)
        log.info(f"[rocket:api-login] {request.user} login")
        return JsonResponse({"loginToken": auth_token})
    except PermissionError:
        log.warning("[rocket:api-login] Login attempt by invalid RC user: {exc}")
        return HttpResponse(status=401)
    except Exception as exc:
        msg = "[rocket:api-login] Exception raised when user attempted an API rocket chat login, "
        msg += f"{exc.__name__.__class__}: {exc}"
        log.error(msg)
        return HttpResponse(status=401)
